from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()
TEMPLATES_URL_NAMES = {
    'about/author.html': '/about/author/',
    'about/tech.html': '/about/tech/'
}


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_page_availability(self):
        """Доступность URL для любого пользователя"""
        for adress in TEMPLATES_URL_NAMES.values():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, adress in TEMPLATES_URL_NAMES.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
