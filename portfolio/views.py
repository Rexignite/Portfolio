from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Project, Profile, Skill, Education, Experience, ContactMessage
from .forms import ProjectUploadForm, ContactForm, ProfileForm
import os
import json

# ===== HOME PAGE =====
def index(request):
    """Home page view"""
    projects = Project.objects.filter(is_featured=True)[:6]
    skills = Skill.objects.all()
    
    # Get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)
    
    context = {
        'projects': projects,
        'skills': skills,
        'profile': profile,
        'page_title': 'Home',
    }
    return render(request, 'index.html', context)


# ===== PROJECT LIST =====
def project_list(request):
    """View all projects"""
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'portfolio/project_list.html', {'projects': projects})


# ===== PROJECT DETAIL =====
def project_detail(request, project_id):
    """View single project"""
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'portfolio/project_detail.html', {'project': project})


# ===== UPLOAD PROJECT =====
@login_required
def upload_project(request):
    """Upload a new project"""
    if request.method == 'POST':
        form = ProjectUploadForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, f'✅ Project "{project.title}" uploaded successfully!')
            return redirect('portfolio:project_list')
        else:
            messages.error(request, '❌ Error uploading project. Please check the form.')
    else:
        form = ProjectUploadForm()
    
    return render(request, 'portfolio/project_upload.html', {'form': form})


# ===== DELETE PROJECT =====
@login_required
def delete_project(request, project_id):
    """Delete a project"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, '✅ Project deleted successfully!')
        return redirect('portfolio:project_list')
    return render(request, 'portfolio/project_confirm_delete.html', {'project': project})


# ===== CONTACT - WITH DATABASE SAVE =====
def contact(request):
    """Contact form view with database save"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validation
        if not name or not email or not message:
            messages.error(request, '❌ Name, Email, and Message are required!')
            return render(request, 'contact.html')
        
        try:
            # ==== SAVE TO DATABASE ====
            contact_msg = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject if subject else 'No Subject',
                message=message
            )
            print(f"✅ Message saved to database: ID {contact_msg.id}")
            
            # ==== SEND EMAIL ====
            try:
                send_mail(
                    f"Portfolio Contact: {subject if subject else 'New Message'}",
                    f"From: {name}\nEmail: {email}\n\nMessage:\n{message}\n\n---\nThis message has been saved in the database (ID: {contact_msg.id})",
                    settings.DEFAULT_FROM_EMAIL,
                    ['riteshyadav.22564@gmail.com'],
                    fail_silently=False,
                )
                print("✅ Email sent successfully")
            except Exception as e:
                print(f"⚠️ Email error: {str(e)}")
            
            messages.success(request, '✅ Your message has been sent successfully!')
            return redirect('portfolio:contact')
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            messages.error(request, f'❌ Error: {str(e)}')
            return render(request, 'contact.html')
    
    return render(request, 'contact.html')


# ===== VIEW ALL MESSAGES (ADMIN) =====
@login_required
def view_messages(request):
    """View all contact messages - Admin only"""
    if not request.user.is_superuser:
        messages.error(request, '❌ Access denied! Admin only.')
        return redirect('portfolio:index')
    
    messages_list = ContactMessage.objects.all()
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    
    # Mark as read if requested
    if request.GET.get('mark_read'):
        try:
            msg = ContactMessage.objects.get(id=request.GET.get('mark_read'))
            msg.mark_as_read()
            messages.success(request, '✅ Message marked as read!')
        except ContactMessage.DoesNotExist:
            pass
    
    context = {
        'messages_list': messages_list,
        'unread_count': unread_count,
        'total_count': messages_list.count(),
    }
    return render(request, 'portfolio/view_messages.html', context)


# ===== DELETE MESSAGE =====
@login_required
def delete_message(request, message_id):
    """Delete a contact message - Admin only"""
    if not request.user.is_superuser:
        messages.error(request, '❌ Access denied! Admin only.')
        return redirect('portfolio:index')
    
    msg = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == 'POST':
        msg.delete()
        messages.success(request, '✅ Message deleted successfully!')
        return redirect('portfolio:view_messages')
    
    return render(request, 'portfolio/delete_message.html', {'message': msg})


# ===== REPLY TO MESSAGE =====
@login_required
def reply_message(request, message_id):
    """Reply to a contact message - Admin only"""
    if not request.user.is_superuser:
        messages.error(request, '❌ Access denied! Admin only.')
        return redirect('portfolio:index')
    
    msg = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == 'POST':
        reply_text = request.POST.get('reply', '').strip()
        
        if reply_text:
            try:
                # Send reply email
                send_mail(
                    f"Re: {msg.subject}",
                    f"Dear {msg.name},\n\n{reply_text}\n\n---\n\nBest regards,\nRitesh Kumar\nBackend Developer\n\nOriginal Message:\n{msg.message}",
                    settings.DEFAULT_FROM_EMAIL,
                    [msg.email],
                    fail_silently=False,
                )
                msg.mark_as_replied()
                messages.success(request, f'✅ Reply sent to {msg.email}!')
                return redirect('portfolio:view_messages')
            except Exception as e:
                messages.error(request, f'❌ Error sending reply: {str(e)}')
        else:
            messages.error(request, '❌ Please enter a reply!')
    
    return render(request, 'portfolio/reply_message.html', {'message': msg})


# ===== UPLOAD PROFILE PICTURE (AJAX) - NEW =====
@login_required
@csrf_exempt
def upload_profile_pic(request):
    """Upload profile picture via AJAX from home page"""
    if request.method == 'POST' and request.FILES.get('profile_pic'):
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
            file = request.FILES['profile_pic']
            
            # Validate file size (5MB)
            if file.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'message': 'File too large! Maximum 5MB allowed.'
                })
            
            # Validate file type
            if not file.content_type.startswith('image/'):
                return JsonResponse({
                    'success': False,
                    'message': 'Please select an image file!'
                })
            
            # Delete old photo if exists
            if profile.profile_pic:
                profile.profile_pic.delete()
            
            profile.profile_pic = file
            profile.save()
            
            return JsonResponse({
                'success': True,
                'image_url': profile.profile_pic.url,
                'message': 'Photo uploaded successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request!'
    })


# ===== UPDATE BIO - NEW =====
@login_required
def update_bio(request):
    """Update user bio from home page"""
    if request.method == 'POST':
        profile, created = Profile.objects.get_or_create(user=request.user)
        bio = request.POST.get('bio', '').strip()
        profile.bio = bio
        profile.save()
        messages.success(request, '✅ Bio updated successfully!')
    return redirect('portfolio:index')


# ===== EDIT PROFILE (Optional - Keep for backward compatibility) =====
@login_required
def edit_profile(request):
    """Edit user profile with photo upload and removal (Legacy)"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle photo removal
        if request.POST.get('remove_photo') == 'true':
            if profile.profile_pic:
                profile.profile_pic.delete()
                profile.save()
                messages.success(request, '✅ Profile photo removed!')
                return redirect('portfolio:edit_profile')
        
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated successfully!')
            return redirect('portfolio:index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'portfolio/edit_profile.html', {'form': form, 'profile': profile})


# ===== RESUME DOWNLOAD =====
def download_resume(request):
    """Download resume file"""
    try:
        profile = Profile.objects.first()
        if profile and profile.resume:
            # Check if file exists
            if os.path.exists(profile.resume.path):
                response = FileResponse(open(profile.resume.path, 'rb'), as_attachment=True)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(profile.resume.name)}"'
                return response
            else:
                messages.error(request, '❌ Resume file not found on server!')
        else:
            messages.error(request, '❌ Resume not found! Please upload one.')
        return redirect('portfolio:index')
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
        return redirect('portfolio:index')


# ===== API ENDPOINTS =====

def api_projects(request):
    """API endpoint for projects"""
    projects = Project.objects.all().order_by('-created_at')
    data = []
    for project in projects:
        data.append({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'image': project.image.url if project.image else None,
            'github_link': project.github_link,
            'live_link': project.live_link,
            'tags': project.get_tags_list(),
            'created_at': project.created_at.strftime('%Y-%m-%d'),
        })
    return JsonResponse({'projects': data})


def upload_project_ajax(request):
    """AJAX file upload endpoint"""
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            
            # Validate file size (50MB max)
            if file.size > 50 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'message': 'File too large! Maximum 50MB allowed.'
                })
            
            file_name = default_storage.save(f'uploads/{file.name}', ContentFile(file.read()))
            file_url = default_storage.url(file_name)
            
            return JsonResponse({
                'success': True,
                'message': 'File uploaded successfully!',
                'file_url': file_url,
                'file_name': file.name
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request!'
    })


# ===== TEST VIEW =====
def test_email(request):
    """Test email configuration"""
    try:
        send_mail(
            'Test Email from Portfolio',
            'This is a test email from your Django portfolio.',
            settings.DEFAULT_FROM_EMAIL,
            ['riteshyadav.22564@gmail.com'],
            fail_silently=False,
        )
        messages.success(request, '✅ Test email sent successfully!')
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    return redirect('portfolio:index')