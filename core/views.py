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

class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    template_name = 'core/category_form.html'
    fields = ['name', 'slug']
    success_url = reverse_lazy('category-list')

class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    template_name = 'core/category_form.html'
    fields = ['name', 'slug']
    success_url = reverse_lazy('category-list')

class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'core/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')


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
        else:
            context['is_enrolled'] = False
        return context

class CourseCreateView(AdminRequiredMixin, CreateView):
    model = Course
    template_name = 'core/course_form.html'
    fields = ['category', 'title', 'description', 'cover_image']
    success_url = reverse_lazy('course-list')

class CourseUpdateView(AdminRequiredMixin, UpdateView):
    model = Course
    template_name = 'core/course_form.html'
    fields = ['category', 'title', 'description', 'cover_image']
    success_url = reverse_lazy('course-list')

class CourseDeleteView(AdminRequiredMixin, DeleteView):
    model = Course
    template_name = 'core/course_confirm_delete.html'
    success_url = reverse_lazy('course-list')


from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.db.models import Count
from .models import Enrollment, Lesson, User
from django import forms

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.prefetch_related(
            models.Prefetch('courses', queryset=Course.objects.annotate(enrollment_count=Count('enrollments')))
        )
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
        # Ensure user is enrolled
        if not Enrollment.objects.filter(user=self.request.user, course=lesson.course).exists():
            context['not_enrolled'] = True
        else:
            context['all_lessons'] = lesson.course.lessons.all()
        return context

class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-zinc-900 border border-zinc-800 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-white'
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

def register_view(request):
    if request.method == 'POST':
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
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
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
