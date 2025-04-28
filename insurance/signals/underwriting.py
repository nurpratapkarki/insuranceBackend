from django.dispatch import receiver
from insurance.models import Underwriting
from django.db.models.signals import post_save

@receiver(post_save, sender=Underwriting)
def update_policy_holder_from_underwriting(sender, instance, **kwargs):
    """Update PolicyHolder's risk category based on Underwriting."""
    # Skip updates if manual_override is enabled
    if instance.manual_override:
        return

    policy_holder = instance.policy_holder

    # Only update if the risk category has changed
    if policy_holder.risk_category != instance.risk_category:
        policy_holder.risk_category = instance.risk_category
        policy_holder.save()