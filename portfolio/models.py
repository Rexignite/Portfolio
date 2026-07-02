from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ============================================================
# 1. CONTACT MESSAGE MODEL
# ============================================================
class ContactMessage(models.Model):
    """Store contact form messages"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.name} - {self.email}"
    
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.save()
    
    def mark_as_replied(self):
        """Mark message as replied"""
        self.is_replied = True
        self.replied_at = timezone.now()
        self.save()


# ============================================================
# 2. PROFILE MODEL
# ============================================================
class Profile(models.Model):
    """User profile with photo and resume"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, help_text="Short bio about yourself")
    profile_pic = models.ImageField(
        upload_to='profile/', 
        null=True, 
        blank=True,
        help_text="Upload your profile photo (JPG, PNG)"
    )
    resume = models.FileField(
        upload_to='resumes/', 
        null=True, 
        blank=True,
        help_text="Upload your resume (PDF only)"
    )
    github = models.URLField(blank=True, help_text="GitHub profile URL")
    linkedin = models.URLField(blank=True, help_text="LinkedIn profile URL")
    email = models.EmailField(blank=True, help_text="Contact email")
    phone = models.CharField(max_length=20, blank=True, help_text="Phone number")
    location = models.CharField(max_length=100, blank=True, help_text="City, Country")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


# ============================================================
# 3. PROJECT MODEL
# ============================================================
class Project(models.Model):
    """Portfolio projects"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(
        upload_to='projects/images/', 
        null=True, 
        blank=True,
        help_text="Project screenshot (JPG, PNG)"
    )
    file = models.FileField(
        upload_to='projects/files/', 
        null=True, 
        blank=True,
        help_text="Project files (PDF, ZIP)"
    )
    github_link = models.URLField(blank=True, null=True, help_text="GitHub repository URL")
    live_link = models.URLField(blank=True, null=True, help_text="Live demo URL")
    tags = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="Comma separated tags: Django, Python, React"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """Return tags as list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_short_description(self, length=100):
        """Get short description"""
        if len(self.description) > length:
            return self.description[:length] + '...'
        return self.description


# ============================================================
# 4. SKILL MODEL
# ============================================================
class Skill(models.Model):
    """Skills with levels"""
    SKILL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='intermediate')
    order = models.IntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"
    
    def get_level_percentage(self):
        """Convert level to percentage"""
        levels = {
            'beginner': 25,
            'intermediate': 50,
            'advanced': 75,
            'expert': 100,
        }
        return levels.get(self.level, 50)


# ============================================================
# 5. EDUCATION MODEL
# ============================================================
class Education(models.Model):
    """Education details"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year = models.CharField(max_length=20, help_text="e.g., 2022-2025")
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Education'
        verbose_name_plural = 'Educations'
    
    def __str__(self):
        return f"{self.degree} - {self.institution}"


# ============================================================
# 6. EXPERIENCE MODEL
# ============================================================
class Experience(models.Model):
    """Work experience"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    order = models.IntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', '-start_date']
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def get_duration(self):
        """Get duration in years/months"""
        if self.end_date:
            delta = self.end_date - self.start_date
        else:
            delta = timezone.now().date() - self.start_date
        
        years = delta.days // 365
        months = (delta.days % 365) // 30
        
        if years > 0 and months > 0:
            return f"{years}y {months}m"
        elif years > 0:
            return f"{years}y"
        elif months > 0:
            return f"{months}m"
        return "Less than 1 month"
    
    def get_date_range(self):
        """Get formatted date range"""
        start = self.start_date.strftime('%b %Y')
        if self.is_current or not self.end_date:
            end = 'Present'
        else:
            end = self.end_date.strftime('%b %Y')
        return f"{start} - {end}"


# ============================================================
# 7. TESTIMONIAL MODEL (Optional - Extra)
# ============================================================
class Testimonial(models.Model):
    """Client testimonials"""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
    
    def __str__(self):
        return f"{self.name} - {self.company or 'Client'}"