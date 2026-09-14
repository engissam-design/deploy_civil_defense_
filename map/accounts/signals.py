from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    groups_to_create = ["Super Admin", "Governorate Admin", "Center Admin", "Category Admin", "User"]
    for name in groups_to_create:
        Group.objects.get_or_create(name=name)
