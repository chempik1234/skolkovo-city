import base64

from django.contrib import admin
from django.utils.html import format_html, escape

from django import forms
from django.utils.safestring import mark_safe

from .forms import ImageArrayWidget
from .models import Category, TelegramUser


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'images_urls': ImageArrayWidget(),
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title_ru', 'title_en', 'parent')
    list_filter = ('parent',)
    search_fields = ('title_ru', 'title_en',)
    prepopulated_fields = {}
    readonly_fields = ('images_urls_display',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['images_urls'].widget = ImageArrayWidget()
        return form

    def images_urls_display(self, obj):
        if not obj.images_urls:
            return "-"

        images = []
        for url in obj.images_urls:
            if url:
                images.append(
                    f'<img src="{escape(url.strip())}" style="max-width: 200px; max-height: 200px; margin: 5px;">'
                )

        return format_html('<div style="display: flex; flex-wrap: wrap;">{}</div>',
                           mark_safe("".join(images)))

    images_urls_display.short_description = "Изображения"


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('telegram_id',)
