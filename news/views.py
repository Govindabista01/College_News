from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.text import slugify
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import Article, Category, Comment
from .forms import LoginForm, RegisterForm, ArticleForm, CommentForm, CategoryForm
from django.views.decorators.csrf import csrf_exempt

def is_admin(user):
    """Check if user is an admin (staff or superuser)"""
    return user.is_staff or user.is_superuser

def handler403(request, exception=None):
    """Custom 403 error handler for non-admin users"""
    return render(request, '403.html', status=403)

def home(request):
    """Home page with latest published articles"""
    articles = Article.objects.filter(status='published').select_related('author', 'category')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        articles = articles.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    # Get recent articles for sidebar
    recent_articles = Article.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-published_at')[:5]
    
    # Get popular articles for sidebar
    popular_articles = Article.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-views')[:5]
    
    # Get latest article for header
    latest_article = Article.objects.filter(
        status='published'
    ).order_by('-published_at').first()
    
    # Calculate stats
    total_articles = Article.objects.filter(status='published').count()
    total_categories = Category.objects.count()
    total_views = sum(article.views for article in Article.objects.filter(status='published'))
    total_likes = sum(article.likes.count() for article in Article.objects.filter(status='published'))
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'recent_articles': recent_articles,
        'popular_articles': popular_articles,
        'latest_article': latest_article,
        'total_articles': total_articles,
        'total_categories': total_categories,
        'total_views': total_views,
        'total_likes': total_likes,
    }
    return render(request, 'home.html', context)

@login_required
def article_detail(request, slug):
    """Display individual article with comments"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    # Increment view count
    article.views += 1
    article.save(update_fields=['views'])
    
    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.is_approved = True  # Auto-approve comments
            comment.save()
            messages.success(request, 'Comment posted successfully!')
            return redirect('article_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    # Get all comments (since they're auto-approved)
    comments = article.comments.all()
    
    # Get related articles (same category, published, excluding current article)
    related_articles = Article.objects.filter(
        category=article.category,
        status='published'
    ).exclude(pk=article.pk).order_by('-published_at')[:5]
    
    # Get popular articles for sidebar
    popular_articles = Article.objects.filter(
        status='published'
    ).exclude(pk=article.pk).order_by('-views')[:5]
    
    # Get previous and next articles
    try:
        previous_article = Article.objects.filter(
            status='published',
            published_at__lt=article.published_at
        ).order_by('-published_at').first()
    except:
        previous_article = None
    
    try:
        next_article = Article.objects.filter(
            status='published',
            published_at__gt=article.published_at
        ).order_by('published_at').first()
    except:
        next_article = None
    
    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
        'related_articles': related_articles,
        'popular_articles': popular_articles,
        'previous_article': previous_article,
        'next_article': next_article,
    }
    return render(request, 'article_detail.html', context)

def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to College News Portal, {user.username}! You can now like and comment on articles.')
            return redirect('home')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard for authenticated users"""
    user_articles = Article.objects.filter(author=request.user).order_by('-created_at')
    
    # Basic stats
    user_articles_count = user_articles.count()
    total_views = sum(article.views for article in user_articles)
    total_likes = sum(article.likes.count() for article in user_articles)
    total_comments = sum(article.comments.count() for article in user_articles)
    
    # Performance metrics
    avg_views = user_articles_count and total_views // user_articles_count or 0
    avg_likes = user_articles_count and total_likes // user_articles_count or 0
    
    # Calculate engagement rate (likes + comments / views)
    total_engagement = total_likes + total_comments
    engagement_rate = total_views and min(100, (total_engagement / total_views) * 100) or 0
    
    # Recent comments on user's articles
    recent_comments = Comment.objects.filter(
        article__author=request.user
    ).select_related('author', 'article').order_by('-created_at')[:5]
    
    # Popular categories
    from django.db.models import Count
    popular_categories = Category.objects.annotate(
        article_count=Count('articles')
    ).order_by('-article_count')[:5]
    
    # Recent activities (simplified for now)
    recent_activities = []
    for article in user_articles[:3]:
        recent_activities.append({
            'description': f'Created article "{article.title}"',
            'timestamp': article.created_at,
            'icon': 'newspaper',
            'color': 'primary'
        })
    
    # Popular articles (by views)
    popular_articles = Article.objects.filter(
        status='published'
    ).order_by('-views')[:5]
    
    # Get total users for sidebar badge
    total_users = User.objects.count()
    
    context = {
        'user_articles': user_articles,
        'user_articles_count': user_articles_count,
        'total_views': total_views,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'avg_views': avg_views,
        'avg_likes': avg_likes,
        'avg_views_percentage': min(100, avg_views * 10),  # Simple percentage calculation
        'avg_likes_percentage': min(100, avg_likes * 20),  # Simple percentage calculation
        'engagement_rate': round(engagement_rate, 1),
        'recent_comments': recent_comments,
        'popular_categories': popular_categories,
        'recent_activities': recent_activities,
        'popular_articles': popular_articles,
        'total_users': total_users,
    }
    return render(request, 'dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def article_list(request):
    """List all articles for the current user or all if admin/staff"""
    if request.user.is_superuser or request.user.is_staff:
        articles = Article.objects.all().order_by('-created_at')
    else:
        articles = Article.objects.filter(author=request.user).order_by('-created_at')

    # Search functionality
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )

    # Status filter
    status = request.GET.get('status')
    if status:
        articles = articles.filter(status=status)

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'selected_status': status,
    }
    return render(request, 'article_list.html', context)

@login_required
@user_passes_test(is_admin)
def article_create(request):
    """Create a new article"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.slug = slugify(article.title)
            article.save()
            messages.success(request, 'Article created successfully!')
            return redirect('article_list')
    else:
        form = ArticleForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'article_form.html', context)

@login_required
@user_passes_test(is_admin)
def article_edit(request, slug):
    """Edit an existing article"""
    article = get_object_or_404(Article, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.slug = slugify(article.title)
            article.save()
            messages.success(request, 'Article updated successfully!')
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    
    context = {
        'form': form,
        'article': article,
        'action': 'Edit',
    }
    return render(request, 'article_form.html', context)

@login_required
@user_passes_test(is_admin)
def article_delete(request, slug):
    """Delete an article"""
    article = get_object_or_404(Article, slug=slug, author=request.user)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted successfully!')
        return redirect('article_list')
    
    return render(request, 'article_confirm_delete.html', {'article': article})

@login_required
@user_passes_test(is_admin)
def category_list(request):
    """List all categories"""
    categories = Category.objects.all().order_by('name')
    return render(request, 'category_list.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'category_form.html', context)

@login_required
@user_passes_test(is_admin)
def category_edit(request, pk):
    """Edit an existing category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'action': 'Edit',
    }
    return render(request, 'category_form.html', context)

@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')
    
    return render(request, 'category_confirm_delete.html', {'category': category})

@login_required
def like_unlike(request, slug):
    """Like or unlike an article"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    if request.method == 'POST':
        if article.is_liked_by(request.user):
            # Unlike
            article.likes.remove(request.user)
            messages.info(request, 'Article unliked!')
        else:
            # Like
            article.likes.add(request.user)
            messages.success(request, 'Article liked!')
    
    return redirect('article_detail', slug=slug)

@login_required
def comment_edit(request, comment_id):
    """Edit a comment"""
    comment = get_object_or_404(Comment, pk=comment_id)
    
    # Check if user can edit this comment (author or admin)
    if not (request.user == comment.author or request.user.is_staff):
        messages.error(request, 'You do not have permission to edit this comment.')
        return redirect('article_detail', slug=comment.article.slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('article_detail', slug=comment.article.slug)
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form,
        'comment': comment,
        'article': comment.article,
        'action': 'Edit',
    }
    return render(request, 'comment_form.html', context)

@login_required
def comment_delete(request, comment_id):
    """Delete a comment"""
    comment = get_object_or_404(Comment, pk=comment_id)
    
    # Check if user can delete this comment (author or admin)
    if not (request.user == comment.author or request.user.is_staff):
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('article_detail', slug=comment.article.slug)
    
    if request.method == 'POST':
        article_slug = comment.article.slug
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('article_detail', slug=article_slug)
    
    context = {
        'comment': comment,
        'article': comment.article,
    }
    return render(request, 'comment_confirm_delete.html', context)

@login_required
def comment_create(request, slug):
    """Create a new comment on an article"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.is_approved = True  # Auto-approve comments
            comment.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'id': comment.id,
                        'content': comment.content,
                        'author': comment.author.username,
                    }
                })
            return redirect('article_detail', slug=slug)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Invalid form'}, status=400)
    return redirect('article_detail', slug=slug)

# User Management Views
@login_required
@user_passes_test(is_admin)
def user_list(request):
    """List all users for admin management"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filter by staff status
    staff_filter = request.GET.get('staff')
    if staff_filter == 'true':
        users = users.filter(is_staff=True)
    elif staff_filter == 'false':
        users = users.filter(is_staff=False, is_superuser=False)
    
    paginator = Paginator(users, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Stats
    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    active_users = User.objects.filter(is_active=True).count()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'staff_filter': staff_filter,
        'total_users': total_users,
        'staff_users': staff_users,
        'active_users': active_users,
    }
    return render(request, 'user_list.html', context)

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """View user details and manage user"""
    user_obj = get_object_or_404(User, pk=user_id)
    
    # Get user's articles and comments
    user_articles = Article.objects.filter(author=user_obj).order_by('-created_at')[:5]
    user_comments = Comment.objects.filter(author=user_obj).order_by('-created_at')[:5]
    
    # Stats
    total_articles = user_obj.articles.count()
    total_comments = user_obj.comments.count()
    total_likes = sum(article.likes.count() for article in user_obj.articles.all())
    
    context = {
        'user_obj': user_obj,
        'user_articles': user_articles,
        'user_comments': user_comments,
        'total_articles': total_articles,
        'total_comments': total_comments,
        'total_likes': total_likes,
    }
    return render(request, 'user_detail.html', context)

@login_required
@user_passes_test(is_admin)
def user_toggle_staff(request, user_id):
    """Toggle staff status for a user"""
    if request.method == 'POST':
        user_obj = get_object_or_404(User, pk=user_id)
        user_obj.is_staff = not user_obj.is_staff
        user_obj.save()
        
        status = "admin" if user_obj.is_staff else "regular user"
        messages.success(request, f'{user_obj.username} is now a {status}.')
        
    return redirect('user_detail', user_id=user_id)

@login_required
@user_passes_test(is_admin)
def user_toggle_active(request, user_id):
    """Toggle active status for a user"""
    if request.method == 'POST':
        user_obj = get_object_or_404(User, pk=user_id)
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        
        status = "activated" if user_obj.is_active else "deactivated"
        messages.success(request, f'{user_obj.username} has been {status}.')
        
    return redirect('user_detail', user_id=user_id)

@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    """Delete a user (with confirmation)"""
    user_obj = get_object_or_404(User, pk=user_id)
    
    # Prevent admin from deleting themselves
    if user_obj == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_detail', user_id=user_id)
    
    if request.method == 'POST':
        # Get user info before deletion for the success message
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f'User "{username}" has been deleted successfully.')
        return redirect('user_list')
    
    # Get user's content for confirmation page
    user_articles = user_obj.articles.all()
    user_comments = user_obj.comments.all()
    
    context = {
        'user_obj': user_obj,
        'user_articles': user_articles,
        'user_comments': user_comments,
    }
    return render(request, 'user_confirm_delete.html', context)

# Settings Views
@login_required
@user_passes_test(is_admin)
def settings_view(request):
    """Site settings management"""
    context = {
        'site_name': 'College News Portal',
        'site_description': 'Your trusted source for campus updates',
        'contact_email': 'admin@collegenews.com',
        'total_articles': Article.objects.count(),
        'total_users': User.objects.count(),
        'total_categories': Category.objects.count(),
    }
    return render(request, 'settings.html', context)

# Profile Views
@login_required
def profile_view(request):
    """User profile management"""
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    # Get user stats
    user_articles = Article.objects.filter(author=request.user).order_by('-created_at')[:5]
    user_comments = Comment.objects.filter(author=request.user).order_by('-created_at')[:5]
    
    # Stats
    total_articles = request.user.articles.count()
    total_comments = request.user.comments.count()
    total_likes = sum(article.likes.count() for article in request.user.articles.all())
    
    context = {
        'user_articles': user_articles,
        'user_comments': user_comments,
        'total_articles': total_articles,
        'total_comments': total_comments,
        'total_likes': total_likes,
    }
    return render(request, 'profile.html', context)

# About and Contact Views
def about_view(request):
    """About page"""
    context = {
        'total_articles': Article.objects.count(),
        'total_users': User.objects.count(),
        'total_categories': Category.objects.count(),
    }
    return render(request, 'about.html', context)

def contact_view(request):
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        # For now, we'll just show a success message
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'contact.html')

@csrf_exempt  # For demo; for production, use CSRF token in AJAX
def ajax_delete_comment(request, comment_id):
    if request.method == 'POST':
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.delete()
            return JsonResponse({'success': True})
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Comment not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)