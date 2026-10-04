from django.shortcuts import render
from django.views import generic
from django.views.generic import ListView, DetailView, CreateView
from .models import Post, Author, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect

# Create your views here.

class HomeView(generic.TemplateView):
    template_name = 'blog/index.html'


    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['latest_posts']=Post.objects.order_by('-created_at')[:5]
        context['num_authors']=Author.objects.count()
        context['num_posts']=Post.objects.count()
        return context

class PostListView(ListView):
    model=Post
    template_name='blog/post-list.html'
    context_object_name='post_list'
    paginate_by=5

    def get_queryset(self):
        return Post.objects.order_by('-created_at')

class PostDetailView(DetailView):
    model=Post
    template_name='blog/post-detail.html'
    context_object_name='post'

class AuthorListView(ListView):
    model=Author
    template_name='blog/author-list.html'
    context_object_name='author_list'
    paginate_by=5

    def get_queryset(self):
        return Author.objects.order_by('last_name')

class AuthorDetailView(DetailView):
    model=Author
    template_name='blog/author-detail.html'
    context_object_name='author'

class CommentCreateView(LoginRequiredMixin, CreateView):
    model=Comment
    template_name='blog/comment_form.html'
    fields=['description']

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_obj
        return context
    
    def form_valid(self,form):
        form.instance.post=self.post_obj
        form.instance.author=self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.post_obj.get_absolute_url()

