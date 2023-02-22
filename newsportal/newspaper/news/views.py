from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.core.mail import send_mail
from .filters import PostFilter
from .forms import NewsForm, ProfileUserForm
from .models import *


def index(request):
    news = Post.objects.all()[::-1]
    paginator = Paginator(news, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/listnews.html', context={'page_obj': page_obj})


def detail(request, pk):
    new = Post.objects.get(pk__iexact=pk)
    return render(request, 'news/detail.html', context={'new': new})


def news_search(request):
    f = PostFilter(request.GET, queryset=Post.objects.all())
    return render(request, 'news/search.html', context={'filter': f})


class MyView(PermissionRequiredMixin, View):
    permission_required = ('news.add_post',
                           'news.delete_post',
                           'news.view_post',
                           'news.change_post',)


class NewsCreate(PermissionRequiredMixin, CreateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/news_edit.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.categoryType = 'NW'

        send_mail(
            subject=post.title,
            message=post.text,
            from_email='vitaly.buel@yandex.ru',
            recipient_list=['vitalybuel@gmail.com', ]
        )

        return super().form_valid(form)


class NewsUpdate(PermissionRequiredMixin, UpdateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/news_edit.html'
    permission_required = ('news.change_post',)


class NewsDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/news_delete.html'
    success_url = reverse_lazy('index')
    permission_required = ('news.delete_post',)


class ArticleCreate(PermissionRequiredMixin, CreateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/article_edit.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.categoryType = 'AR'
        return super().form_valid(form)


class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/article_edit.html'
    permission_required = ('news.change_post',)


class ArticleDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/article_delete.html'
    success_url = reverse_lazy('index')
    permission_required = ('news.delete_post',)


class ProfileUserUpdate(LoginRequiredMixin, UpdateView):
    form_class = ProfileUserForm
    model = User
    template_name = 'news/profile_edit.html'
    context_object_name = 'profile'


class CategoryListView(ListView):
    model = Post
    template_name = 'news/category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category).order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context
