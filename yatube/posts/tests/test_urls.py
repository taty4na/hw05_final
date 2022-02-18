from http import HTTPStatus

from django.test import TestCase, Client

from ..models import Group, Post, User


class PostsURLTests(TestCase):
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
        # Создаем пользователя
        cls.user = User.objects.create_user(username='HasNoName')

    def setUp(self):
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Создаем клиент для автора
        self.authorized_author = Client()
        # Авторизуем автора
        self.authorized_author.force_login(self.author_post)

    def test_create_post(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_post_guest(self):
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_post(self):
        response = self.authorized_author.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_available_and_correct_template(self):
        """Проверяет доступность URL-адресов и соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author_post}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
