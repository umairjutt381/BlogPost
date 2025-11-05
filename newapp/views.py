from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm


def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('newapp:register')
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'User registered successfully!')
        return redirect('newapp:login')
    return render(request, 'newapp/register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('newapp:post_list')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('newapp:login')
    return render(request, 'newapp/login.html')


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_superuser and  user != request.user:
        messages.error(request, 'You dont have permission to delete user')
        return redirect('show_context')
    user.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('show_context')

@login_required
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_superuser and user != request.user:
        messages.error(request, 'You dont have permission to update this user')
        return redirect('newapp:show_context')

    if request.method == 'POST':
        new_password = request.POST['password']
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password updated successfully!')
        return redirect('newapp:show_context')

    return render(request, 'newapp/update.html', {'user': user})


def show_context(request):
    if request.user.is_superuser:
        users = User.objects.all()
    else:
        users = User.objects.filter(id=request.user.id)
    registered_users = {
        user.id: {
            'username': user.username,
            'email': user.email if user.email else 'N/A' ,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M')
        }
        for user in users
    }
    context = {'registered_users': registered_users,'is_admin': request.user.is_superuser}
    return render(request, 'newapp/context.html', context)


def logout_user(request):
    logout(request)
    return redirect('newapp:login')

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_superuser and  user != request.user:
        messages.error(request, 'You dont have permission to delete user')
        return redirect('show_context')
    user.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('show_context')

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'newapp/post_list.html', {'posts': posts})

@login_required
def post_create(request):
    if not request.user.is_superuser:
        messages.info(request, "You can create your own post.")
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect('newapp:post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'newapp/post_form.html', {'form': form})


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect('newapp:post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()

    return render(request, 'newapp/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if not request.user.is_superuser and request.user != post.author:
        messages.error(request, "You don’t have permission to edit this post.")
        return redirect('newapp:post_detail', pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('newapp:post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'newapp/post_form.html', {'form': form})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user.is_superuser or request.user == post.author:
        post.delete()
        messages.success(request, "Post deleted successfully!")
    else:
        messages.error(request, "You don’t have permission to delete this post.")
    return redirect('newapp:post_list')