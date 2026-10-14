from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    telegram = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return self.username

class SiteSettings(models.Model):
    copyright_text = models.CharField(max_length=255)
    telegram_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        if SiteSettings.objects.exists() and not self.pk:
            # if you'll not check for self.pk
            # then error will also raised in update of exists model
            raise ValidationError('There can be only one SiteSettings instance')
        return super(SiteSettings, self).save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='courses/covers/')

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    video_url = models.URLField(blank=True, null=True)
    content = models.TextField(blank=True)
    lesson_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['lesson_order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"
