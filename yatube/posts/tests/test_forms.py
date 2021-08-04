import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post, User

URLS = (
    reverse('posts:index'),
    reverse('posts:new_post')
)
TEXT = {
    'for_edit': 'Текст редактируемого поста',
    'new_post': 'Тестовый текст',
    'post_edit': 'Исправленный текст'
}
USERNAMES = {'author': 'Автор', 'authorized_client': 'TestUser'}

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.form = PostForm()
        cls.user = User.objects.create(username=USERNAMES['author'])
        cls.post = Post.objects.create(
            text=TEXT['for_edit'],
            author=cls.user,
            id=1
        )
        cls.URLS = (
            reverse(
                'posts:post_edit',
                kwargs={'username': cls.post.author, 'post_id': cls.post.id}
            ),
            reverse(
                'posts:post',
                kwargs={'username': cls.post.author, 'post_id': cls.post.id}
            )
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.user = User.objects.create_user(
            username=USERNAMES['authorized_client']
        )
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostFormTests.user)

    def test_create_new_post(self):
        """
        При отправке формы создаётся новая запись в базе данных.
        Пользователь перенаправляется на главную страницу.
        """
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {'text': TEXT['new_post'], 'image': uploaded}
        response = self.authorized_client.post(
            URLS[1],
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, URLS[0])
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.first().text, TEXT['new_post'])
        self.assertEqual(Post.objects.first().author, self.user)
        self.assertIsNone(Post.objects.first().group)
        self.assertEqual(Post.objects.first().image, 'posts/small.gif')

    def test_edit_post(self):
        """
        При редактировании поста через форму на странице
        /<username>/<post_id>/edit/
        изменяется соответствующая запись в базе данных.
        """
        posts_count = Post.objects.count()
        edit_data = {'text': TEXT['post_edit']}
        response = self.author_client.post(
            PostFormTests.URLS[0],
            data=edit_data,
            follow=True
        )
        self.assertRedirects(response, PostFormTests.URLS[1])
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=TEXT['post_edit'],
                author=PostFormTests.user,
                group=None
            ).exists()
        )
