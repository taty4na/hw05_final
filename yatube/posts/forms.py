from django.forms import ModelForm, Textarea, Select

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        widgets = {
            "text": Textarea(attrs={
                'class': 'form-control',
                'cols': '40',
                'rows': '10'
            }),
            "group": Select(attrs={'class': 'form-control'})
        }

        labels = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = {'text'}
        widgets = {
            "text": Textarea(attrs={
                'class': 'form-control',
                'cols': '40',
                'rows': '10'
            }),
        }
