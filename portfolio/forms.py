from django import forms
from .models import Project, Profile, ContactMessage

# ===== PROJECT UPLOAD FORM =====
class ProjectUploadForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'image', 'file', 'github_link', 'live_link', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project title...'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Describe your project...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.zip,.rar'
            }),
            'github_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username/project'
            }),
            'live_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-project.com'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Django, Python, Bootstrap, API'
            }),
        }
        help_texts = {
            'image': 'Upload a project screenshot (JPG, PNG)',
            'file': 'Upload project files (PDF, ZIP)',
            'tags': 'Separate tags with commas',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError('Title must be at least 3 characters long.')
        return title

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if tags:
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if len(tags_list) > 10:
                raise forms.ValidationError('Maximum 10 tags allowed.')
        return tags


# ===== CONTACT FORM =====
class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name...',
            'required': True
        }),
        error_messages={
            'required': 'Please enter your name.',
            'max_length': 'Name is too long.'
        }
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'required': True
        }),
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    subject = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject (optional)'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'form-control',
            'placeholder': 'Write your message here...',
            'required': True
        }),
        error_messages={
            'required': 'Please enter your message.'
        }
    )

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        if len(message) > 2000:
            raise forms.ValidationError('Message is too long (max 2000 characters).')
        return message

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Name must be at least 2 characters long.')
        if not name.replace(' ', '').isalpha():
            raise forms.ValidationError('Name should only contain letters and spaces.')
        return name.title()


# ===== PROFILE FORM =====
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'resume', 'bio', 'github', 'linkedin', 'phone', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Tell about yourself...'
            }),
            'github': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/username'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 9876543210'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'profile_pic': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
        }
        help_texts = {
            'profile_pic': 'Upload your profile photo (JPG, PNG)',
            'resume': 'Upload your resume (PDF only)',
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            # Remove spaces, dashes, plus
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10 or len(phone) > 15:
                raise forms.ValidationError('Phone number must be between 10-15 digits.')
        return phone


# ===== CONTACT MESSAGE FORM (Admin) =====
class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message', 'is_read', 'is_replied']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'is_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_replied': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ===== REPLY FORM =====
class ReplyForm(forms.Form):
    reply = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Write your reply here...',
            'required': True
        }),
        label='Your Reply',
        error_messages={
            'required': 'Please enter a reply.'
        }
    )
    
    def clean_reply(self):
        reply = self.cleaned_data.get('reply', '').strip()
        if len(reply) < 5:
            raise forms.ValidationError('Reply must be at least 5 characters long.')
        if len(reply) > 2000:
            raise forms.ValidationError('Reply is too long (max 2000 characters).')
        return reply