import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

def validate_image_file(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions are: .jpg, .jpeg, .png, .webp')

    # 5MB limit
    limit = 5 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MB.')

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
    site_name = models.CharField(max_length=150, default='Yangidev')
    logo = models.ImageField(upload_to='site/', blank=True, null=True, validators=[validate_image_file])

    hero_title = models.CharField(max_length=255, default="Kelajak kasblarini biz bilan o'rganing")
    hero_description = models.TextField(default="Eng zamonaviy texnologiyalar, amaliy loyihalar va tajribali ustozlar yordamida dasturlashni noldan professional darajagacha o'rganing.")

    copyright_text = models.CharField(max_length=255, default='© 2026 Yangidev. Barcha huquqlar himoyalangan.')

    telegram_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    support_title = models.CharField(max_length=255, default="Loyihani qo'llab-quvvatlash")
    support_description = models.TextField(default="Platformamiz rivoji va yangi bepul darsliklar chiqishiga o'z hissangizni qo'shing.")
    support_url = models.URLField(blank=True, null=True, default='https://t.me/yangidev', help_text="Link for supporting/donating to the project")

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
    cover_image = models.ImageField(upload_to='courses/covers/', validators=[validate_image_file])

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

class Instructor(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='instructors/', blank=True, null=True, validators=[validate_image_file])
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {'Completed' if self.is_completed else 'In Progress'}"

class DatabaseMediaFile(models.Model):
    name = models.CharField(max_length=255, unique=True)
    content = models.BinaryField()
    content_type = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
