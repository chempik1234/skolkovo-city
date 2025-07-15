from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from ckeditor.fields import RichTextField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    description = RichTextField(blank=True, null=True)
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
