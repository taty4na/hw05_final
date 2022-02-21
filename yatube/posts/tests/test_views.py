from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User, Comment
from ..utils import POSTS_SOW


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.author_post,
                text=f'{i} ПамагитеПамагите',
                group=cls.group,
            )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author_post)
        authorized_client = User.objects.create_user(username='follower')
        self.authorized_client = Client()
        self.authorized_client.force_login(authorized_client)

    def test_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.author_post}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        # Проверяем, вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_obj(self):
        """Paginator формирует страницы."""
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.author_post}),
        ]
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse):
                response = self.authorized_author.get(reverse_name)
                self.assertEqual(len(
                    response.context['page_obj']), POSTS_SOW)
                response = self.authorized_author.get(reverse_name + '?page=2')
                self.assertEqual(len(
                    response.context['page_obj']),
                    (Post.objects.count() % POSTS_SOW))

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse('posts:index'))
        # Проверяем, что тип объекта соответствуют ожиданиям
        self.assertIsInstance(response.context['page_obj'][0], Post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        # Проверяем, что тип объекта соответствуют ожиданиям
        self.assertIsInstance(response.context['page_obj'][0], Post)
        # Проверяем соответствие группе
        self.assertEqual(response.context['page_obj'][0].group, self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:profile', kwargs={'username': self.author_post}))
        # Проверяем, что тип объекта соответствуют ожиданиям
        self.assertIsInstance(response.context['page_obj'][0], Post)
        # Проверяем соответствие автору
        self.assertEqual(response.
                         context['page_obj'][0].author, self.author_post)
        self.assertEqual(response.context.get('user').posts.count(), 13)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        # Проверяем, что тип объекта соответствуют ожиданиям
        self.assertIsInstance(response.context['post'], Post)
        # Проверяем соответствие id
        self.assertEqual(response.context['post'].id, self.post.id)

    def test_create_and_edit_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        pages_names = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        ]
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse):
                response = self.authorized_author.get(reverse_name)
                # Проверяем, типы полей формы в словаре context соответствуют
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form').fields.get(value)
                        # Проверяет, что поле формы является экземпляром
                        # указанного класса
                        self.assertIsInstance(form_field, expected)

    def test_create_comment(self):
        """Комментарий появляется на странице поста."""
        form = {
            'text': ('Саид, спасибо за ревью! '
                     'у меня не все пока получается, '
                     'поэтому очень радуют понятные и логичные замечания, '
                     'которые действительно помогают разобраться')
        }
        comments_count = Comment.objects.count()
        response = self.authorized_author.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form,
            follow=True,
        )
        response = self.authorized_author.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        text_comment = response.context['comments'][0]
        self.assertEqual(Comment.objects.last(), text_comment)

        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form,
            follow=True,
        )
        self.assertRedirects(response, '/auth/login/?next=/posts/13/comment/')

    def test_follower(self):
        """Формирование ленты избранных авторов."""
        # Без подписки нет ленты избрынных авторов
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertFalse(response.context['page_obj'])
        #  Подписываемся
        response = self.authorized_client.post(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author_post}),
            follow=True,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertTrue(response.context['page_obj'])
        # Дизлайк атписка
        response = self.authorized_client.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author_post}),
            follow=True,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertFalse(response.context['page_obj'])
