from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Напишите текст вашего поста здесь.',
            'group': 'Выберите группу.',
            'image': 'Можете добавить картинку.',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Напишите ваш комментарий здесь.',
        }
