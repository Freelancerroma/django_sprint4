from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User

NUMS_OF_POST_DISPLAY = 10


class PostListView(ListView):
    """Страница постов сайта"""

    model = Post
    template_name = 'blog/index.html'
    queryset = Post.time_pub.select_related(
        'category', 'location', 'author'
    ).filter(
            category__is_published=True,
    ).annotate(
            comment_count=Count('comments')
    )
    ordering = '-pub_date'
    paginate_by = NUMS_OF_POST_DISPLAY


class PostDetailView(DetailView):
    """Страница отдельной публикации"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        post = get_object_or_404(
            Post.objects.filter(
                id=self.kwargs['post_id']
            )
        )
        if post.author == self.request.user:
            return Post.objects.filter(id=self.kwargs['post_id'])
        return Post.time_pub.filter(id=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.filter(
            post=self.object.id
        ).order_by(
            'created_at'
        )
        return context


class PostCategoryView(ListView):
    """Страница постов выбранной категории"""

    model = Post
    template_name = 'blog/category.html'
    ordering = '-pub_date'
    paginate_by = NUMS_OF_POST_DISPLAY

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        self.category_posts = get_object_or_404(
            Category.objects.filter(
                is_published=True,
                slug=category_slug,
            )
        )
        return super().get_queryset().filter(
            category=self.category_posts,
            pub_date__lte=timezone.now(),
            is_published=True,
        ).annotate(
            comment_count=Count('comments')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category_posts
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Страница создания поста"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование поста"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление поста"""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs['post_id']
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class UserListView(ListView):
    """Страница пользователя"""

    model = User
    template_name = 'blog/profile.html'
    paginate_by = NUMS_OF_POST_DISPLAY

    def get_queryset(self):
        user_name = self.kwargs['username']
        self.author = get_object_or_404(
            User.objects.filter(
                username=user_name,
            )
        )
        if self.author == self.request.user:
            return Post.objects.select_related(
                'category', 'location', 'author'
            ).filter(
                author=self.author
            ).order_by(
                '-pub_date'
            ).annotate(
                comment_count=Count('comments')
            )
        return Post.time_pub.select_related(
            'category', 'location', 'author'
            ).filter(
            author=self.author, category__is_published=True,
            ).order_by(
            '-pub_date'
            ).annotate(
            comment_count=Count('comments')
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """"Страница редактирования профиля"""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария к посту"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.posts = get_object_or_404(
            Post.objects.filter(
                id=self.kwargs['post_id']
            )
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.posts
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование комментария"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment.objects.filter(
                id=kwargs['comment_id']
            )
        )
        if instance.author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление комментария"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment.objects.filter(
                id=kwargs['comment_id']
            )
        )
        if instance.author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
