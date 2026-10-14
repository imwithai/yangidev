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
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Course URLs
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),

    path('courses/<int:pk>/enroll/', views.EnrollView.as_view(), name='course-enroll'),
    path('lessons/<int:pk>/', views.ClassroomView.as_view(), name='classroom'),
    path('lessons/<int:pk>/complete/', views.CompleteLessonView.as_view(), name='lesson-complete'),
]
