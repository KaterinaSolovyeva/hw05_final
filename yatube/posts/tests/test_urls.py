from django.test import Client, TestCase
from posts.models import Group, Post, User

GROUP_TITLE = 'Заголовок тестовой группы'
GROUP_SLUG = 'test-slug'
POST_TEXT = 'Текст тестового поста'
POST_ID = 1
USERNAMES = {'author': 'TestUser', 'authorized_client': 'Kate'}
URL_NAMES = {
    'for_guests': (
        '/',
        f'/group/{GROUP_SLUG}/',
        f'/{USERNAMES["author"]}/',
        f'/{USERNAMES["author"]}/{POST_ID}/'
    ),
    'for_authorized_users': (
        '/new/',
        f'/{USERNAMES["author"]}/{POST_ID}/edit/',
        f'/{USERNAMES["author"]}/{POST_ID}/comment/'
    )
}
TEMPLATES_URL_NAMES = {
    '/': 'posts/index.html',
    f'/group/{GROUP_SLUG}/': 'posts/group.html',
    '/new/': 'posts/new.html',
    f'/{USERNAMES["author"]}/{POST_ID}/edit/': 'posts/new.html'
}


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG
        )
        cls.user = User.objects.create(username=USERNAMES['author'])
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
            id=POST_ID
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(
            username=USERNAMES['authorized_client']
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostsURLTests.user)

    def test_page_availability(self):
        """Доступность URL для любого пользователя."""
        for url in URL_NAMES['for_guests']:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_new_post(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            URL_NAMES['for_authorized_users'][0]
        )
        self.assertEqual(response.status_code, 200)

    def test_urls_for_authorized_redirect_anonymous_on_admin_login(self):
        """URL для авторизированных пользователей перенаправит анонимного
        пользователя на страницу логина.
        """
        for url in URL_NAMES['for_authorized_users']:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}')

    def test_edit_post(self):
        """Страница редактирования поста доступна только его автору,
        а другого пользователя перенаправляет на страницу поста.
        """
        response = self.author_client.get(
            URL_NAMES['for_authorized_users'][1]
        )
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get(
            URL_NAMES['for_authorized_users'][1],
            follow=True
        )
        self.assertRedirects(response, URL_NAMES['for_guests'][3])

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for adress, template in TEMPLATES_URL_NAMES.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_comment_for_authorized(self):
        """Комментирование поста доступно авторизованному пользователю."""
        response = self.authorized_client.get(
            URL_NAMES['for_authorized_users'][2]
        )
        self.assertEqual(response.status_code, 200)
