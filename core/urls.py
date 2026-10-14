from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category-add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),

    # Course URLs
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/add/', views.CourseCreateView.as_view(), name='course-add'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course-edit'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course-delete'),

    path('courses/<int:pk>/enroll/', views.EnrollView.as_view(), name='course-enroll'),
    path('lessons/<int:pk>/', views.ClassroomView.as_view(), name='classroom'),
]
