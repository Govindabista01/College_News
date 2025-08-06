from django.urls import path
from . import views
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Comment

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('article/<slug:slug>/like/', views.like_unlike, name='article_like'),  # Fixed name
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard and management (requires login)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Article management
    path('articles/', views.article_list, name='article_list'),
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<slug:slug>/edit/', views.article_edit, name='article_update'),  # Fixed name and parameter
    path('articles/<slug:slug>/delete/', views.article_delete, name='article_delete'),  # Fixed parameter
    
    # Category management
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Comment management
    path('comments/<int:comment_id>/edit/', views.comment_edit, name='comment_update'),  # Fixed name
    path('comments/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('article/<slug:slug>/comment/', views.comment_create, name='comment_create'),  # Added missing comment creation
    
    # User Management (Admin only)
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-staff/', views.user_toggle_staff, name='user_toggle_staff'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # Settings (Admin only)
    path('settings/', views.settings_view, name='settings'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # About and Contact
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # AJAX delete comment
    path('comments/delete/<int:comment_id>/', views.ajax_delete_comment, name='ajax_delete_comment'),
]
