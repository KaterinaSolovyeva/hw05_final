from django.test import Client, TestCase
from django.urls import reverse

TEMPLATES_REVERSE_NAMES = {
    'about/author.html': reverse('about:author'),
    'about/tech.html': reverse('about:tech')
}


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемыe приложением about доступны."""
        for reverse_name in TEMPLATES_REVERSE_NAMES.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """При запросе к view-функциям  применяются ожидаемые шаблоны."""
        for template, reverse_name in TEMPLATES_REVERSE_NAMES.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
