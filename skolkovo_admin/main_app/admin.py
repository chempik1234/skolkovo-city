from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Category, TelegramUser
from ckeditor.widgets import CKEditorWidget
from django import forms


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(),
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ('title', 'parent')
    list_filter = ('parent',)
    search_fields = ('title', 'description')
    prepopulated_fields = {}


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'full_name', 'email', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('telegram_id', 'full_name', 'email')
