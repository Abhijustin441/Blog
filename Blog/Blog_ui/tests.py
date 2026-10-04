from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import datetime

from .models import Author, Post, Comment


class AuthorModelTest(TestCase):
    def test_str_is_first_last_name(self):
        author = Author.objects.create(first_name='Ada', last_name='Lovelace')
        self.assertEqual(str(author), 'Ada Lovelace')

    def test_get_absolute_url(self):
        author = Author.objects.create(first_name='Ada', last_name='Lovelace')
        self.assertEqual(author.get_absolute_url(), f'/blog/blogger/{author.id}')


class PostModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='Ada', last_name='Lovelace')

    def test_ordering_is_newest_first(self):
        older = Post.objects.create(
            title='Older', author=self.author, content='...',
            created_at=timezone.now() - datetime.timedelta(days=1)
        )
        newer = Post.objects.create(
            title='Newer', author=self.author, content='...',
            created_at=timezone.now()
        )
        posts = list(Post.objects.all())
        self.assertEqual(posts[0], newer)
        self.assertEqual(posts[1], older)

    def test_get_absolute_url(self):
        post = Post.objects.create(title='Test', author=self.author, content='...')
        self.assertEqual(post.get_absolute_url(), f'/blog/{post.id}')


class CommentModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='Ada', last_name='Lovelace')
        self.post = Post.objects.create(title='Test', author=self.author, content='...')
        self.user = User.objects.create_user(username='commenter', password='pass12345')

    def test_ordering_is_oldest_first(self):
        first = Comment.objects.create(
            post=self.post, author=self.user, description='First',
            created_at=timezone.now() - datetime.timedelta(hours=1)
        )
        second = Comment.objects.create(
            post=self.post, author=self.user, description='Second',
            created_at=timezone.now()
        )
        comments = list(self.post.comments.all())
        self.assertEqual(comments[0], first)
        self.assertEqual(comments[1], second)

    def test_str_truncates_to_75_chars(self):
        long_text = 'x' * 100
        comment = Comment.objects.create(
            post=self.post, author=self.user, description=long_text
        )
        self.assertEqual(len(str(comment)), 75)
        self.assertEqual(str(comment), 'x' * 75)


class PostListViewTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='Ada', last_name='Lovelace')
        for i in range(7):
            Post.objects.create(title=f'Post {i}', author=self.author, content='...')

    def test_paginated_by_five(self):
        response = self.client.get(reverse('Blog_ui:post-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['post_list']), 5)

    def test_second_page_has_remainder(self):
        response = self.client.get(reverse('Blog_ui:post-list') + '?page=2')
        self.assertEqual(len(response.context['post_list']), 2)


class AuthorDetailViewTest(TestCase):
    def test_not_paginated(self):
        author = Author.objects.create(first_name='Ada', last_name='Lovelace')
        for i in range(10):
            Post.objects.create(title=f'Post {i}', author=author, content='...')
        response = self.client.get(reverse('Blog_ui:author-detail', args=[author.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('is_paginated', response.context)
        self.assertEqual(len(response.context['author'].posts.all()), 10)


class CommentCreateViewTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='Ada', last_name='Lovelace')
        self.post = Post.objects.create(title='Test', author=self.author, content='...')
        self.user = User.objects.create_user(username='commenter', password='pass12345')
        self.create_url = reverse('Blog_ui:comment-create', args=[self.post.id])

    def test_logged_out_redirects_to_login_with_next(self):
        response = self.client.get(self.create_url)
        self.assertRedirects(
            response,
            f'/accounts/login/?next={self.create_url}',
            fetch_redirect_response=False,
        )

    def test_logged_in_can_view_form(self):
        self.client.login(username='commenter', password='pass12345')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.post)

    def test_posting_comment_sets_post_and_author(self):
        self.client.login(username='commenter', password='pass12345')
        response = self.client.post(self.create_url, {'description': 'Nice post!'})
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(description='Nice post!')
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)

    def test_posting_comment_redirects_to_post_detail(self):
        self.client.login(username='commenter', password='pass12345')
        response = self.client.post(self.create_url, {'description': 'Nice post!'})
        self.assertRedirects(response, self.post.get_absolute_url())

    def test_logged_out_cannot_post(self):
        comment_count_before = Comment.objects.count()
        self.client.post(self.create_url, {'description': 'Should not save'})
        self.assertEqual(Comment.objects.count(), comment_count_before)