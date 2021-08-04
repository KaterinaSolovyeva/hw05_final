from django.test import TestCase
from posts.models import Group, Post, User

GROUP_TITLE = 'Заголовок тестовой группы'
GROUP_SLUG = 'test-group'
GROUP_DESCRIPTION = 'Описание тестовой группы'
USERNAME = 'Тестовый автор'
POST_TEXT = 'Текст тестового поста'


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )

    def test_object_name_is_title_field(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=USERNAME
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user
        )

    def test_object_name_is_title_field(self):
        """__str__  post - это строчка с первыми 15 символами post.text."""
        post = PostModelTest.post
        expected_object_name = f'{post.text[:15]}...'
        self.assertEqual(expected_object_name, str(post))
