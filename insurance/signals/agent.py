from django.dispatch import receiver
from insurance.models import AgentApplication, SalesAgent
from django.db.models.signals import post_save
from decimal import Decimal
from datetime import date

@receiver(post_save, sender=AgentApplication)
def agent_application_approval(sender, instance, created, **kwargs):
    """Create SalesAgent when application is approved."""
    try:
        if instance.status.upper() == "APPROVED" and not SalesAgent.objects.filter(application=instance).exists():
            agent_code = f"A-{instance.branch.id}-{str(instance.id).zfill(4)}"
            SalesAgent.objects.create(
                branch=instance.branch,
                application=instance,
                agent_code=agent_code,
                commission_rate=Decimal('5.00'),  # Default commission rate
                is_active=True,
                joining_date=date.today(),
                status='ACTIVE'
            )
    except Exception as e:
        print(f"Error in agent_application_approval signal: {str(e)}")
        raise

            
    except Exception as e:
        print(f"Error in agent_application_approval signal: {str(e)}")
        raise  # Re-raise the exception to ensure it's not silently ignored
