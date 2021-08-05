from django.test import TestCase
from posts.models import Comment, Follow, Group, Post, User

GROUP_TITLE = 'Заголовок тестовой группы'
GROUP_SLUG = 'test-group'
GROUP_DESCRIPTION = 'Описание тестовой группы'
USERNAME = 'Тестовый автор'
COMMENTATOR = 'Автор комментария'
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
        cls.user = User.objects.create(username=USERNAME)
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user
        )

    def test_object_name_is_title_field(self):
        """__str__  post - это строчка с первыми 15 символами post.text."""
        post = PostModelTest.post
        expected_object_name = f'{post.text[:15]}...'
        self.assertEqual(expected_object_name, str(post))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user
        )
        cls.commentator = User.objects.create(username=COMMENTATOR)
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.commentator,
            text=POST_TEXT
        )

    def test_object_name_is_title_field(self):
        """
        __str__  comment - это строчка с первыми 
        15 символами comment.text.
        """
        comment = CommentModelTest.comment
        expected_object_name = f'{comment.text[:15]}...'
        self.assertEqual(expected_object_name, str(comment))


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=USERNAME)
        cls.user = User.objects.create(username=COMMENTATOR)
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_object_name_is_title_field(self):
        """
        __str__ follow - это строчка:
        '<имя фолловера> подписан на <имя автора поста>'.
        """
        follow = FollowModelTest.follow
        expected_object_name = f'{follow.user} подписан на {follow.author}'
        self.assertEqual(expected_object_name, str(follow))
