import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post

User = get_user_model()


GROUP_TITLE = 'Test group'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Описание'
GROUP_B_TITLE = 'Another group'
GROUP_B_DESCRIPTION = 'Описание второй группы'
GROUP_B_SLUG = 'another-slug'
USERNAMES = {
    'author': 'Автор',
    'authorized_client': 'TestUser',
    'not_follower': 'No'
}
POST_TEXT = 'Текст тестового поста'
CACHE_TEXT = 'Текст для кэша'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
URLS = (
    reverse('posts:index'),
    reverse('posts:group_posts', kwargs={'slug': GROUP_SLUG}),
    reverse(
        'posts:profile',
        kwargs={'username': USERNAMES['authorized_client']}
    ),
    reverse('posts:new_post'),
    reverse('posts:follow_index')
)
TEMPLATES_PAGES_NAMES = {
    'posts/index.html': reverse('posts:index'),
    'posts/group.html': (
        reverse('posts:group_posts', kwargs={'slug': GROUP_SLUG})
    ),
    'posts/new.html': reverse('posts:new_post'),
}


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            description=GROUP_DESCRIPTION,
            slug=GROUP_SLUG
        )
        cls.another_group = Group.objects.create(
            title=GROUP_B_TITLE,
            description=GROUP_B_DESCRIPTION,
            slug=GROUP_B_SLUG
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.user = User.objects.create(username=USERNAMES['authorized_client'])
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.URLS = (
            reverse(
                'posts:post_edit',
                kwargs={'username': cls.post.author, 'post_id': cls.post.id}
            ),
            reverse(
                'posts:post',
                kwargs={'username': cls.post.author, 'post_id': cls.post.id}
            ),
            reverse(
                'posts:add_comment',
                kwargs={'username': cls.post.author, 'post_id': cls.post.id}
            ),
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(PostPagesTests.user)

    def test_post_with_group_appears_on_page(self):
        """
        Новый пост, с указанной группой, появляется на странице этой
        группы и на главной странице.
        """
        for url in URLS[0:2]:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn(
                    PostPagesTests.post, response.context.get('page')
                )

    def test_post_not_appears_on_another_page(self):
        """Пост не появляется на странице чужой группы."""
        response = self.author_client.get(
            reverse('posts:group_posts', kwargs={'slug': GROUP_B_SLUG})
        )
        self.assertNotIn(
            PostPagesTests.post, response.context.get('page')
        )

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in TEMPLATES_PAGES_NAMES.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(URLS[0])
        first_object = response.context['page'][0]
        author_0 = first_object.author
        text_0 = first_object.text
        image_0 = first_object.image
        self.assertEqual(author_0, self.user)
        self.assertEqual(text_0, PostPagesTests.post.text)
        self.assertEqual(image_0, PostPagesTests.post.image)

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.guest_client.get(URLS[1])
        self.assertEqual(
            response.context['group'].title,
            PostPagesTests.group.title
        )
        self.assertEqual(
            response.context['group'].description,
            PostPagesTests.group.description
        )
        self.assertEqual(
            response.context['group'].slug,
            PostPagesTests.group.slug
        )
        first_object = response.context['page'][0]
        author_0 = first_object.author
        text_0 = first_object.text
        image_0 = first_object.image
        self.assertEqual(author_0, self.user)
        self.assertEqual(text_0, PostPagesTests.post.text)
        self.assertEqual(image_0, PostPagesTests.post.image)

    def test_new_post_pages_show_correct_context(self):
        """Шаблон new_post и post_edit сформированы с правильным контекстом."""
        response_edit = self.author_client.get(PostPagesTests.URLS[0])
        response_new_post = self.author_client.get(URLS[3])
        responses = (response_edit, response_new_post)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                for response in responses:
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформированы с правильным контекстом."""
        response = self.guest_client.get(URLS[2])
        self.assertEqual(
            response.context['author'], PostPagesTests.post.author
        )
        first_object = response.context['page'][0]
        author_0 = first_object.author
        text_0 = first_object.text
        image_0 = first_object.image
        self.assertEqual(author_0, PostPagesTests.post.author)
        self.assertEqual(text_0, PostPagesTests.post.text)
        self.assertEqual(image_0, PostPagesTests.post.image)

    def test_post_pages_show_correct_context(self):
        """Шаблон post сформированы с правильным контекстом."""
        response = self.guest_client.get(PostPagesTests.URLS[1])
        self.assertEqual(
            response.context['author'],
            PostPagesTests.post.author
        )
        self.assertEqual(
            response.context['post'].text, PostPagesTests.post.text
        )
        self.assertEqual(
            response.context['post'].image,
            PostPagesTests.post.image
        )
    
    def test_new_post_pages_show_correct_context(self):
        """Шаблон add_comment сформирован с правильным контекстом."""
        response = self.author_client.get(PostPagesTests.URLS[2])
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """Список записей хранится в кэше и обновлялся раз в 20 секунд."""
        Post.objects.create(text=CACHE_TEXT, author=PostPagesTests.user)
        response = self.author_client.get(URLS[0])
        self.assertNotContains(response, CACHE_TEXT)
        cache.clear()
        response = self.author_client.get(URLS[0])
        self.assertContains(response, CACHE_TEXT)


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            description=GROUP_DESCRIPTION,
            slug=GROUP_SLUG
        )
        cls.user = User.objects.create(username=USERNAMES['author'])
        cls.objs = (
            Post(
                text=POST_TEXT + str(i),
                author=cls.user,
                group=cls.group
            ) for i in range(0, 13)
        )
        Post.objects.bulk_create(cls.objs)

    def setUp(self):
        self.guest_client = Client()

    def test_paginator(self):
        """
        На первой странице отображается settings.NUMBER_OF_POSTS постов,
        3 переносятся на вторую.
        """
        for reverse_name in URLS[0:2]:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page']), settings.NUMBER_OF_POSTS
                )
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page']), 3)


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAMES['author'])
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
        )

    def setUp(self):
        self.follower_client = Client()
        self.user_follower = User.objects.create_user(
            username=USERNAMES['authorized_client']
        )
        self.follower_client.force_login(self.user_follower)
        self.notfollower_client = Client()
        self.user = User.objects.create_user(
            username=USERNAMES['not_follower']
        )
        self.notfollower_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(FollowViewsTests.user)

    def test_follow_unfollow(self):
        """
        Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок.
        Новая запись пользователя появляется в ленте тех, кто на
        него подписан и не появляется в ленте тех, кто не подписан на него.
        """
        Follow.objects.create(
            user=self.user_follower,
            author=FollowViewsTests.user
        )
        response = self.follower_client.get(URLS[4])
        self.assertIn(FollowViewsTests.post, response.context.get('page'))
        response = self.notfollower_client.get(URLS[4])
        self.assertNotIn(FollowViewsTests.post, response.context.get('page'))
        Follow.objects.filter(
            user=self.user_follower,
            author=FollowViewsTests.user
        ).delete()
        response = self.follower_client.get(URLS[4])
        self.assertNotIn(FollowViewsTests.post, response.context.get('page'))
