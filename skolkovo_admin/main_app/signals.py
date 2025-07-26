from django.core.files.storage import default_storage
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from main_app.models import Video, Question, Category


@receiver(pre_save, sender=Video)
def delete_old_file(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = Video.objects.get(pk=instance.pk)
    except Video.DoesNotExist:
        return
    old_file = old_instance.file
    new_file = instance.file

    if old_file and old_file != new_file:
        if default_storage.exists(old_file.name):
            default_storage.delete(old_file.name)


@receiver(post_save, sender=Video)
def rename_uploaded_file(sender, instance, created, **kwargs):
    if created and instance.file:
        instance.rename_file()
        instance.save()


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if default_storage.exists(instance.file.name):
            default_storage.delete(instance.file.name)


@receiver(pre_save, sender=Question)
def delete_embedding_for_question(sender, instance, **kwargs):
    if instance.id is None:
        return

    prev_object = Question.objects.get(id=instance.id)
    if prev_object.question != instance.question:
        instance.embedding = None


@receiver(post_save, sender=Category)
def create_question_for_category(sender, instance, created, **kwargs):
    if created:
        Question.objects.create(question=instance.title_ru, category=instance)
