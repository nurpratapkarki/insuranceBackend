from contextvars import Token
from datetime import date, timezone
from decimal import Decimal
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.db import transaction
from insurance.models import AgentReport, Bonus, Customer, PolicyHolder, PremiumPayment, Underwriting


# Signal handlers for PolicyHolder model to create premium payments
@receiver(post_save, sender=PolicyHolder)
def policy_holder_post_save(sender, instance, created, **kwargs):
    """Handle post-save operations for PolicyHolder."""
    try:
        with transaction.atomic():
            # Create PremiumPayment for approved/active policies
            if instance.status in ['Approved', 'Active']:
                premium, created = PremiumPayment.objects.get_or_create(
                    policy_holder=instance,
                    defaults={
                        'payment_interval': instance.payment_interval,
                        'payment_mode': instance.payment_mode
                    }
                )
                if not created:
                    premium.save()  # Ensure calculations are updated
            
    except Exception as e:
        print(f"Error in policy_holder_post_save signal: {str(e)}")


# Signal handlers for PolicyHolder model to create underwriting
@receiver(post_save, sender=PolicyHolder)
def create_or_update_underwriting(sender, instance, created, **kwargs):
    """Create or update underwriting for active or pending policyholders."""
    # Avoid infinite recursion by skipping updates caused by the signal itself
    if getattr(instance, '_from_signal', False):
        return
    
    if instance.status in ['Pending', 'Active']:
        underwriting, _ = Underwriting.objects.get_or_create(policy_holder=instance)

        # Save underwriting without triggering PolicyHolder updates
        underwriting._from_signal = True
        underwriting.save()
        underwriting._from_signal = False


# Signal handlers for PolicyHolder model to update agent statistics
@receiver(post_save, sender=PolicyHolder)
def update_agent_stats_on_new_policy(instance, created):
    """Update agent statistics when a new policy is created"""
    if created and instance.agent:
        with transaction.atomic():
            agent = instance.agent
            
            # Update agent's total policies
            agent.total_policies_sold += 1
            agent.last_policy_date = timezone.now().date()
            agent.save()

            # Create or update the monthly report
            report_date = timezone.now().date()
            report, created = AgentReport.objects.get_or_create(
                agent=agent,
                branch=agent.branch,
                report_date=report_date.replace(day=1),  # First day of current month
                defaults={
                    'reporting_period': f"{report_date.year}-{report_date.month}",
                    'policies_sold': 0,
                    'total_premium': Decimal('0.00'),
                    'commission_earned': Decimal('0.00'),
                    'target_achievement': Decimal('0.00'),
                    'renewal_rate': Decimal('0.00'),
                    'customer_retention': Decimal('0.00'),
                }
            )
            
            report.policies_sold += 1
            report.save()

# Urenewal process
@receiver(post_save, sender=PolicyHolder)
def handle_policy_renewal(instance):
    """
    Handle policy renewal processes
    - Triggered when policy status changes
    - Creates renewal notices
    - Updates related records
    """
    try:
        # Check if policy is near maturity (e.g., within 30 days)
        if instance.maturity_date and instance.status == 'Active':
            today = date.today()
            days_to_maturity = (instance.maturity_date - today).days
            
            if 0 < days_to_maturity <= 30:
                # You can add renewal notification logic here
                pass
                
    except Exception as e:
        print(f"Error in handle_policy_renewal signal: {str(e)}")

# Signal handlers for PolicyHolder model to trigger bonus on anniversary

@receiver(post_save, sender=PolicyHolder)
def trigger_bonus_on_anniversary(sender, instance, created, **kwargs):
    """Automatically credit bonus if the policy is over one year old."""
    today = date.today()

    # Ensure the policy is active and at least one year old
    if instance.status == 'Active' and (today - instance.start_date).days >= 365:
        # Check if a bonus already exists for the current year
        if not Bonus.objects.filter(policy_holder=instance, start_date__year=today.year).exists():
            try:
                # Create the bonus for the current year
               Bonus.objects.create(
                    policy_holder=instance,
                    bonus_type='SI',  # Assuming Simple Interest as default
                    start_date=today
                )
                # The bonus is calculated and saved in the Bonus model's save method
            except Exception as e:
                print(f"Error creating bonus: {e}")

    # Handle backdated policies (if start_date is updated)
    if not created and instance.start_date:
        # Calculate the years since the policy started
        start_year = instance.start_date.year
        current_year = today.year

        for year in range(start_year + 1, current_year + 1):
            # Check if a bonus already exists for the year
            if not Bonus.objects.filter(policy_holder=instance, start_date__year=year).exists():
                try:
                    # Credit bonus for the year
                    Bonus.objects.create(
                        policy_holder=instance,
                        bonus_type='SI',
                        start_date=date(year, instance.start_date.month, instance.start_date.day)
                    )
                    # The bonus is calculated and saved in the Bonus model's save method
                except Exception as e:
                    print(f"Error creating bonus for year {year}: {e}")
       

# Signal handlers for PolicyHolder model to clean up related records
@receiver(pre_delete, sender=PolicyHolder)
def cleanup_policy_holder(sender, instance, **kwargs):
    """
    Clean up related records when PolicyHolder is deleted:
    - Deletes premium payments
    - Deletes underwriting records
    - Removes uploaded documents
    """
    try:
        # Delete related records
        PremiumPayment.objects.filter(policy_holder=instance).delete()
        Underwriting.objects.filter(policy_holder=instance).delete()
        
        # Delete uploaded files
        file_fields = [
            'document_front', 
            'document_back', 
            'pp_photo', 
            'pan_front', 
            'pan_back', 
            'nominee_document_front',
            'nominee_document_back', 
            'nominee_pp_photo',
            'past_medical_report',
            'recent_medical_reports'
        ]
        
        for field in file_fields:
            document = getattr(instance, field, None)
            if document:
                try:
                    document.delete(save=False)
                except Exception as e:
                    print(f"Error deleting {field}: {str(e)}")
                
    except Exception as e:
        print(f"Error in cleanup_policy_holder signal: {str(e)}")
@receiver(post_save, sender=Customer)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create an auth token for the customer when a new customer is created."""
    if created:
        try:
            # Create a new auth token for the customer
            Token.objects.create(user=instance)
        except Exception as e:
            print(f"Error creating auth token: {str(e)}")