from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='ПамагитеПамагите',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group_str = PostModelTest.group.__str__()
        self.assertEqual(group_str, 'Тестовая группа')
        post_str = PostModelTest.post.__str__()
        self.assertEqual(post_str, 'ПамагитеПамагит')
