from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Category, Course

# Category Views
class CategoryListView(ListView):
    model = Category
    template_name = 'core/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(CreateView):
    model = Category
    template_name = 'core/category_form.html'
    fields = ['name', 'slug']
    success_url = reverse_lazy('category-list')

class CategoryUpdateView(UpdateView):
    model = Category
    template_name = 'core/category_form.html'
    fields = ['name', 'slug']
    success_url = reverse_lazy('category-list')

class CategoryDeleteView(DeleteView):
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

class CourseCreateView(CreateView):
    model = Course
    template_name = 'core/course_form.html'
    fields = ['category', 'title', 'description', 'cover_image']
    success_url = reverse_lazy('course-list')

class CourseUpdateView(UpdateView):
    model = Course
    template_name = 'core/course_form.html'
    fields = ['category', 'title', 'description', 'cover_image']
    success_url = reverse_lazy('course-list')

class CourseDeleteView(DeleteView):
    model = Course
    template_name = 'core/course_confirm_delete.html'
    success_url = reverse_lazy('course-list')
