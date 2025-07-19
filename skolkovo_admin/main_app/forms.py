from django import forms
from django.utils.html import escape
from django.utils.safestring import mark_safe


class UrlsArrayWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        if not value:
            value = ""
        value = value.replace("\n", "").replace(',', ',\n\n')
        return mark_safe(f'<textarea style="width: 700px; height: 200px" name="{escape(name)}">{escape(value)}</textarea>')
