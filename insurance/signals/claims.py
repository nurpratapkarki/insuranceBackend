from django.dispatch import receiver
from insurance.models import ClaimProcessing, ClaimRequest, PaymentProcessing
from django.db.models.signals import post_save


@receiver(post_save, sender=ClaimRequest)
def create_claim_processing(sender, instance, created, **kwargs):
    """Create claim processing when a claim request is created."""
    if created:
        ClaimProcessing.objects.create(
            branch=instance.branch,
            claim_request=instance
        )

 #automatically mark the paid onece the payment  is approved
@receiver(post_save, sender=ClaimProcessing)
def auto_finalize_payment(sender, instance, **kwargs):
    if instance.processing_status == 'Approved':
        PaymentProcessing.objects.filter(claim_request=instance.claim_request).update(
            processing_status='Completed'
        )
