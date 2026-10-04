from django.urls import path, include
from . import views

app_name = 'Blog_ui'
urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('blogs', views.PostListView.as_view(), name='post-list'),
    path('blogger/<int:pk>',views.AuthorDetailView.as_view(), name='author-detail'),
    path('blogger/',views.AuthorListView.as_view(), name='author-list'),
    path('<int:pk>', views.PostDetailView.as_view(), name='post-detail'),
    path('blogs/<int:pk>/create/', views.CommentCreateView.as_view(), name='comment-create')
    
]