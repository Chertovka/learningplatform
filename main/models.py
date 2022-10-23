from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from main.utilities import get_timestamp_path
from main.utilities import send_new_comment_notification


class Rubric(models.Model):
    name = models.CharField(max_length=100, db_index=True, unique=True, verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Рубрики'
        verbose_name = 'Рубрика'


class News(models.Model):
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, verbose_name='Рубрика')
    title = models.CharField(max_length=40, verbose_name='Новость')
    content = models.TextField(verbose_name='Описание')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Новости'
        verbose_name = 'Новость'
        ordering = ['-created_at']


class AdditionalImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name='Новость')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

    class Meta:
        verbose_name_plural = 'Дополнительные иллюстрации'
        verbose_name = 'Дополнительная иллюстрация'


class UserProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user_profile__isnull=True)


class UserProfile(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
    send_messages = models.BooleanField(default=True, verbose_name='Слать оповещения об ответах на обращения?')
    USER_PROFILE_TYPE_CHOICES = (
        (1, 'student'),
        (2, 'teacher'),
        (3, 'employee'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_PROFILE_TYPE_CHOICES, verbose_name='Роль', default=False)

    class Meta(AbstractUser.Meta):
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(max_length=40, verbose_name='Тема обращения', default=False)
    content = models.TextField(verbose_name='Текст обращения')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Обращения к ректору'
        verbose_name = 'Обращение к ректору'


def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].user.author
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])


post_save.connect(post_save_dispatcher, sender=Comment)
