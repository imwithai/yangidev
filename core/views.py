from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db import models
from .models import Category, Course

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

# Category Views
class CategoryListView(ListView):
    model = Category
    template_name = 'core/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'core/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = self.get_object().courses.annotate(enrollment_count=models.Count('enrollments'))
        return context

# Course Views
class CourseListView(ListView):
    model = Course
    template_name = 'core/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'core/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['enrollment_count'] = course.enrollments.count()
        context['lessons'] = course.lessons.all()

        if self.request.user.is_authenticated:
            context['is_enrolled'] = course.enrollments.filter(user=self.request.user).exists()
            completed = self.request.user.lesson_progress.filter(lesson__course=course, is_completed=True).values_list('lesson_id', flat=True)
            context['completed_lessons'] = list(completed)
            context['completed_count'] = len(completed)

            # Find next lesson
            if context['lessons'].exists():
                next_lesson = context['lessons'].exclude(id__in=completed).order_by('lesson_order').first()
                if not next_lesson: # If all completed, return the last lesson
                    next_lesson = context['lessons'].order_by('-lesson_order').first()
                context['next_lesson'] = next_lesson
            else:
                context['next_lesson'] = None

            if context['lessons'].count() > 0:
                context['progress_percentage'] = int((len(completed) / context['lessons'].count()) * 100)
            else:
                context['progress_percentage'] = 0
        else:
            context['is_enrolled'] = False
            context['completed_lessons'] = []
            context['completed_count'] = 0
            context['progress_percentage'] = 0
            context['next_lesson'] = context['lessons'].first() if context['lessons'].exists() else None

        return context


from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.db.models import Count
from .models import Enrollment, Lesson, User, Instructor, LessonProgress, DatabaseMediaFile
from django import forms
from django.http import HttpResponse, Http404

def serve_media(request, name):
    try:
        db_file = DatabaseMediaFile.objects.get(name=name)
        response = HttpResponse(db_file.content, content_type=db_file.content_type)
        response['Cache-Control'] = 'public, max-age=31536000'
        return response
    except DatabaseMediaFile.DoesNotExist:
        raise Http404("Media file does not exist")

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.prefetch_related(
            models.Prefetch('courses', queryset=Course.objects.annotate(enrollment_count=Count('enrollments')))
        )
        context['instructors'] = Instructor.objects.all()
        return context

class EnrollView(LoginRequiredMixin, View):
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        Enrollment.objects.get_or_create(user=request.user, course=course)
        return redirect('course-detail', pk=pk)

class ClassroomView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'core/classroom.html'
    context_object_name = 'lesson'

    def get_queryset(self):
        return Lesson.objects.select_related('course').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()

        # Auto-enroll user if they visit classroom directly but aren't enrolled
        Enrollment.objects.get_or_create(user=self.request.user, course=lesson.course)

        all_lessons = lesson.course.lessons.all()
        context['all_lessons'] = all_lessons

        completed = self.request.user.lesson_progress.filter(lesson__course=lesson.course, is_completed=True).values_list('lesson_id', flat=True)
        context['completed_lessons'] = list(completed)
        context['completed_count'] = len(completed)

        if all_lessons.count() > 0:
            context['progress_percentage'] = int((len(completed) / all_lessons.count()) * 100)
        else:
            context['progress_percentage'] = 0

        return context

class CompleteLessonView(LoginRequiredMixin, View):
    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)

        # Auto-enroll if not enrolled
        Enrollment.objects.get_or_create(user=request.user, course=lesson.course)

        # Mark as completed
        progress, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        progress.is_completed = True
        progress.save()

        # Find next lesson
        next_lesson = Lesson.objects.filter(
            course=lesson.course,
            lesson_order__gt=lesson.lesson_order
        ).order_by('lesson_order', 'id').first()

        if not next_lesson:
            next_lesson = Lesson.objects.filter(
                course=lesson.course,
                lesson_order=lesson.lesson_order,
                id__gt=lesson.id
            ).order_by('id').first()

        if next_lesson:
            return redirect('classroom', pk=next_lesson.pk)
        return redirect('course-detail', pk=lesson.course.pk)

class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-zinc-900/50 backdrop-blur-sm border border-white/10 text-white rounded-xl px-4 py-3 focus:outline-none focus:border-white/30 focus:ring-1 focus:ring-white/30 transition-all shadow-inner'
            })
            field.help_text = ''

class UserProfileForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'telegram', 'email']
        labels = {
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'telegram': 'Telegram',
            'email': 'Email',
        }

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user_form = UserProfileForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)
        return render(request, 'core/profile.html', {
            'user_form': user_form,
            'password_form': password_form
        })

    def post(self, request):
        user_form = UserProfileForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(request.user, request.POST)

        if 'update_profile' in request.POST:
            if user_form.is_valid():
                user_form.save()
                return redirect('profile')
        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect('profile')

        return render(request, 'core/profile.html', {
            'user_form': user_form,
            'password_form': password_form
        })

class CustomUserCreationForm(TailwindFormMixin, UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].label = 'Parol'
        if 'password2' in self.fields:
            self.fields['password2'].label = 'Parolni tasdiqlang'

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'telegram')
        labels = {
            'username': 'Username',
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'email': 'Email',
            'telegram': 'Telegram',
        }

class CustomAuthenticationForm(TailwindFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Parol'

class CustomPasswordChangeForm(TailwindFormMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Eski parol'
        self.fields['new_password1'].label = 'Yangi parol'
        self.fields['new_password2'].label = 'Yangi parolni tasdiqlang'

from django.core.cache import cache

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_rate_limit(ip, action):
    key = f"rate_limit_{action}_{ip}"
    attempts = cache.get(key, 0)
    if attempts >= 5:
        return False
    cache.set(key, attempts + 1, timeout=300) # Block for 5 minutes after 5 attempts
    return True

def register_view(request):
    if request.method == 'POST':
        ip = get_client_ip(request)
        if not check_rate_limit(ip, 'register'):
            return render(request, 'core/register.html', {
                'form': CustomUserCreationForm(),
                'error_message': 'Juda ko\'p urinishlar. Iltimos, 5 daqiqadan so\'ng qayta urinib ko\'ring.'
            })

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        ip = get_client_ip(request)
        if not check_rate_limit(ip, 'login'):
            return render(request, 'core/login.html', {
                'form': CustomAuthenticationForm(),
                'error_message': 'Juda ko\'p urinishlar. Iltimos, 5 daqiqadan so\'ng qayta urinib ko\'ring.'
            })

        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            # Clear rate limit on successful login
            cache.delete(f"rate_limit_login_{ip}")
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
