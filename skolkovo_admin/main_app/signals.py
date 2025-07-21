import os

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from main_app.models import Video


@receiver(post_save, sender=Video)
def rename_uploaded_file(sender, instance, created, **kwargs):
    if created and instance.file:
        instance.rename_file()
        instance.save()


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
