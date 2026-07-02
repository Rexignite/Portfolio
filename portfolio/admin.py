from django.contrib import admin
from .models import Profile, Project, ContactMessage, Skill, Education, Experience

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read', 'is_replied']
    list_filter = ['is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_as_read_action', 'mark_as_replied_action']
    
    def mark_as_read_action(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Selected messages marked as read.")
    mark_as_read_action.short_description = "Mark selected as read"
    
    def mark_as_replied_action(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_replied=True, replied_at=timezone.now())
        self.message_user(request, "Selected messages marked as replied.")
    mark_as_replied_action.short_description = "Mark selected as replied"
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'is_replied', 'replied_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'location']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_featured']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['title', 'description', 'tags']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'level']
    list_filter = ['level']

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'year']

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']