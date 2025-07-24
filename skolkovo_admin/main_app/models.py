import os

from django.contrib.postgres.fields import ArrayField
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.db.models import TextField


def file_path_fabric(folder_name: str):
    def get_file_path(instance, filename):
        ext = filename.split('.')[-1]
        new_filename = '{}.{}'.format(instance.id, ext)
        return os.path.join(folder_name, new_filename)

    return get_file_path


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

    order_num = models.IntegerField(
        blank=True, null=False, unique=False,
        verbose_name="Порядковый номер"
    )

    images_urls = ArrayField(
        models.TextField(blank=True),
        blank=True,
        null=True,
        default=list,
        help_text="Список URL изображений",
        verbose_name="Ссылки на изображения (ЧЕРЕЗ ЗАПЯТУЮ)"
    )
    videos_urls = ArrayField(
        models.TextField(blank=True),
        blank=True,
        null=True,
        default=list,
        help_text="Список URL видео",
        verbose_name="Ссылки на видео (ЧЕРЕЗ ЗАПЯТУЮ)"
    )

    def save(self, *args, **kwargs):
        # order num is current max in group + 1 by default
        if self.order_num is None:
            max_order = Category.objects.filter(parent_id=self.parent_id).aggregate(models.Max('order_num'))[
                'order_num__max']
            self.order_num = (max_order or 0) + 1

        if self.id is None:
            max_id = Category.objects.aggregate(models.Max('id'))[
                'id__max']
            self.id = max_id + 1
        super().save(*args, **kwargs)

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


class Video(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    file = models.FileField(upload_to=file_path_fabric("videos"))

    def file_url(self):
        return self.file.url

    def rename_file(self):
        ext = self.file.name.split('.')[-1]
        new_name = f"{self.id}.{ext}"

        if default_storage.exists(self.file.name):
            default_storage.save(new_name, ContentFile(self.file.read()))
            default_storage.delete(self.file.name)

        self.file.name = new_name


class Question(models.Model):
    question = models.TextField(null=False, blank=False)
    answer_ru = models.TextField(null=True, blank=True)
    answer_en = models.TextField(null=True, blank=True)
    embedding = models.BinaryField(null=True, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        db_column='category_id',
        blank=True,
        null=True,
        # related_name='questions',
    )

    class Meta:
        db_table = 'question'
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
