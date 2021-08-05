from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.constraints import UniqueConstraint

User = get_user_model()


class Group(models.Model):
    """Модель сообщества."""
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField('Описание')

    class Meta:
        """Дополнительная информация по управлению моделью Group."""
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """Модель записи."""
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        """Дополнительная информация по управлению моделью Post."""
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return f'{self.text[:15]}...'


class Comment(models.Model):
    """Модель комментирования записей."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField('Текст комментария')
    created = models.DateTimeField('Дата комментария', auto_now_add=True)

    class Meta:
        """Дополнительная информация по управлению моделью Comment."""
        ordering = ('-created',)

    def __str__(self) -> str:
        return f'{self.text[:15]}...'


class Follow(models.Model):
    """Модель подписки на автора."""
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        """Дополнительная информация по управлению моделью Follow."""
        constraints = [
            UniqueConstraint(fields=['user', 'author'], name='follow_unique'),
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
