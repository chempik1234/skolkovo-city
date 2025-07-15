from django.db import models
from django.db.models import TextField


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    description = TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        db_column='parent_id',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(primary_key=True)
    full_name = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    personal_data_agreement = models.BooleanField(default=False)

    def __str__(self):
        return f"Telegram User {self.telegram_id}"

    class Meta:
        db_table = 'user'
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'
