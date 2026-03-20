"""
User signals for LMS System.
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to handle user creation.
    
    Can be extended to create related profiles or send notifications.
    """
    if created:
        # Log user creation
        pass  # TODO: Add logging or notification logic