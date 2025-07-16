from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import TextField


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title_ru = models.CharField(max_length=256)
    title_en = models.CharField(max_length=256, null=True, blank=True)
    description_ru = TextField(blank=True, null=True)
    description_en = TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        db_column='parent_id',
        blank=True,
        null=True,
        related_name='children',
    )

    images_urls = ArrayField(
        models.TextField(blank=True),
        blank=True,
        null=True,
        default=list,
        help_text="Список URL изображений",
        verbose_name="Ссылки на изображения (ЧЕРЕЗ ЗАПЯТУЮ)"
    )

    def __str__(self):
        return f"{self.title_ru} (en={self.title_en})"

    class Meta:
        db_table = 'category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(primary_key=True)
    # full_name = models.CharField(max_length=256, blank=True, null=True)
    # email = models.EmailField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    # personal_data_agreement = models.BooleanField(default=False)
    language = models.CharField(default="ru", null=False, max_length=3)

    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return f"Telegram User {self.telegram_id}"

    class Meta:
        db_table = 'user'
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'
