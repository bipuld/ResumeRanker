from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Company

@receiver(post_save, sender=Company)
def company_verified_handler(sender, instance, created, **kwargs):
    """
    Trigger when company becomes verified
    """
    if created:
        return  # only care about updates

    # check if it was just verified
    if instance.is_verified:
        # update ONLY owner
        instance.members.filter(role="owner").update(
            is_approved=True
        )