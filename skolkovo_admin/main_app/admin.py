from django.contrib import admin

from .models import Category, TelegramUser


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent')
    list_filter = ('parent',)
    search_fields = ('title',)
    prepopulated_fields = {}


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'full_name', 'email', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('telegram_id', 'full_name', 'email')
