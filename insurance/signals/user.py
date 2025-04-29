from django.dispatch import receiver
from insurance.models import User
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)