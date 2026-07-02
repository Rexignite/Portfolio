from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # ===== MAIN PAGES =====
    path('', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    
    # ===== PROJECT MANAGEMENT =====
    path('projects/', views.project_list, name='project_list'),
    path('projects/upload/', views.upload_project, name='upload_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/delete/<int:project_id>/', views.delete_project, name='delete_project'),
    
    # ===== PROFILE - NEW (Home Page Upload) =====
    path('upload-profile-pic/', views.upload_profile_pic, name='upload_profile_pic'),
    path('update-bio/', views.update_bio, name='update_bio'),
    
    # ===== PROFILE & RESUME (Legacy - Optional) =====
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('resume/download/', views.download_resume, name='download_resume'),
    
    # ===== ADMIN - MESSAGE MANAGEMENT =====
    path('messages/', views.view_messages, name='view_messages'),
    path('messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('messages/reply/<int:message_id>/', views.reply_message, name='reply_message'),
    
    # ===== API ENDPOINTS =====
    path('api/projects/', views.api_projects, name='api_projects'),
    path('api/upload/', views.upload_project_ajax, name='upload_project_ajax'),
    
    # ===== TEST =====
    path('test-email/', views.test_email, name='test_email'),
]