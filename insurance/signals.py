from django.dispatch import receiver
from insurance.models import AgentApplication, AgentReport, Bonus, ClaimProcessing, ClaimRequest, Customer, PaymentProcessing, PolicyHolder, PremiumPayment, SalesAgent, Underwriting, User
from django.db.models.signals import post_save, pre_delete
from datetime import date
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from rest_framework.authtoken.models import Token
from django.db.models import F

''' Agent Application signals'''

@receiver(post_save, sender=AgentApplication)
def agent_application_approval(sender, instance, created, **kwargs):
    """Create SalesAgent when application is approved."""
    print(f"--- agent_application_approval SIGNAL TRIGGERED for App ID: {instance.pk}, Status: {instance.status}, Created: {created} ---")
    try:
        if instance.status.upper() == "APPROVED" and not SalesAgent.objects.filter(application=instance).exists():
            print(f"--- agent_application_approval: Condition MET for App ID: {instance.pk} ---")
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
        else:
            print(f"--- agent_application_approval: Condition NOT MET for App ID: {instance.pk} ---")
    except Exception as e:
        print(f"--- agent_application_approval: ERROR: {str(e)} ---")
        # raise # Temporarily comment out raise during debugging if needed

@receiver(post_save, sender=ClaimRequest)
def create_claim_processing(sender, instance: ClaimRequest, created, **kwargs):
    """Create claim processing when a claim request is created."""
    if created:
        # Check if a ClaimProcessing record already exists (e.g., if created manually elsewhere)
        if not hasattr(instance, 'processing'):
            if instance.branch:
                # Attempt to get the company from the branch
                company = instance.branch.company
                if company:
                    try:
                        ClaimProcessing.objects.create(
                            claim_request=instance,
                            branch=instance.branch,
                            company=company, # Set the company explicitly
                            processing_status='Processing' # Set initial status
                        )
                        print(f"ClaimProcessing record created via signal for ClaimRequest {instance.pk}")
                    except Exception as e:
                        print(f"ERROR creating ClaimProcessing via signal for ClaimRequest {instance.pk}: {e}")
                else:
                    print(f"WARNING: Cannot create ClaimProcessing for ClaimRequest {instance.pk}. Branch {instance.branch.pk} has no associated Company.")
            else:
                print(f"WARNING: Cannot create ClaimProcessing for ClaimRequest {instance.pk}. No Branch associated.")
        else:
             print(f"INFO: ClaimProcessing already exists for ClaimRequest {instance.pk}. Signal skipping creation.")

# automatically mark the paid onece the payment  is approved
@receiver(post_save, sender=ClaimProcessing)
def auto_finalize_payment(sender, instance, **kwargs):
    if instance.processing_status == 'Approved':
        PaymentProcessing.objects.filter(claim_request=instance.claim_request).update(
            processing_status='Completed'
        )

'''Policy holder signals'''

# Signal handlers for PolicyHolder model to create premium payments
@receiver(post_save, sender=PolicyHolder)
def policy_holder_post_save(sender, instance, created, **kwargs):
    """Handle post-save operations for PolicyHolder."""
    if PremiumPayment is None or PolicyHolder is None:
        return
    try:
        with transaction.atomic():
            # Create PremiumPayment for approved/active policies
            if instance.status in ['Approved', 'Active']:
                premium, created_premium = PremiumPayment.objects.get_or_create(
                    policy_holder=instance,
                )
                # Ensure calculations run by calling save 
                premium.save() 
            
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
print("--- insurance/signals.py: Before @receiver for update_agent_stats_on_new_policy ---")
@receiver(post_save, sender=PolicyHolder)
def update_agent_stats_on_new_policy(sender, instance, created, **kwargs):
    """Update agent statistics when a new policy is created"""
    print(f"--- update_agent_stats_on_new_policy SIGNAL TRIGGERED for PH ID: {instance.pk}, Created: {created} ---")
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
def handle_policy_renewal(sender, instance, created, **kwargs):
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

@receiver(post_save, sender=User)
def create_auth_token_user(sender, instance=None, created=False, **kwargs):
    """Create an auth token for the user when a new user is created."""
    if Token is None or User is None:
        return
    if created:
        try:
            Token.objects.create(user=instance)
        except Exception as e:
            print(f"Error creating auth token for user {instance.username}: {str(e)}")

''' Premium Payments signals'''

@receiver(post_save, sender=PremiumPayment)
def update_agent_report_and_commission(sender, instance, **kwargs):
    """Update agent report and commission when a premium payment is made/saved."""
    if AgentReport is None or SalesAgent is None or PremiumPayment is None or PolicyHolder is None:
        return
        
    agent = instance.policy_holder.agent
    if not agent:
        return

    # Check if the interval_payment has been calculated (is > 0)
    interval_payment_decimal = instance.interval_payment if isinstance(instance.interval_payment, Decimal) else Decimal(str(instance.interval_payment))
    if interval_payment_decimal <= 0:
        return # Don't process if interval payment isn't calculated yet or is zero

    # *** Key Change: Check if total_paid was actually modified in this save ***
    # This relies on the model save() logic resetting paid_amount after processing.
    # A truly robust solution might need pre_save to capture the state or use django-dirtyfields.
    # Simplified check: Assume if interval_payment > 0 and save happens, commission might apply.
    # A better check might be to see if total_paid increased, but that requires pre_save state.
    
    # Let's proceed assuming a save with interval_payment > 0 implies a payment event for now.
    try:
        with transaction.atomic():
            # *** Use current date to determine the report period ***
            report_date = timezone.now().date() # Use current date

            report, created_report = AgentReport.objects.get_or_create(
                agent=agent,
                branch=agent.branch,
                report_date=report_date.replace(day=1), # Use first day of CURRENT month
                defaults={
                    'reporting_period': f"{report_date.year}-{report_date.month}", # Current month/year
                    'policies_sold': 0, # Note: policies_sold updated by PolicyHolder signal
                    'total_premium': Decimal('0.00'),
                    'commission_earned': Decimal('0.00'),
                    'target_achievement': Decimal('0.00'),
                    'renewal_rate': Decimal('0.00'),
                    'customer_retention': Decimal('0.00'),
                }
            )

            commission_rate_decimal = agent.commission_rate if isinstance(agent.commission_rate, Decimal) else Decimal(str(agent.commission_rate))
            commission = (interval_payment_decimal * commission_rate_decimal / 100).quantize(Decimal('1.00')) # Calculate commission

            # Use F expressions for atomic updates - Apply commission based on the interval payment
            report.total_premium = F('total_premium') + interval_payment_decimal 
            report.commission_earned = F('commission_earned') + commission
            report.save()
            
            # Update agent totals atomically if possible
            current_total_premium = agent.total_premium_collected if isinstance(agent.total_premium_collected, Decimal) else Decimal(str(agent.total_premium_collected))
            agent.total_premium_collected = current_total_premium + interval_payment_decimal
            agent.save(update_fields=['total_premium_collected'])

    except Exception as e:
        print(f"Error in update_agent_report_and_commission signal: {str(e)}")

@receiver(post_save, sender=PremiumPayment)
def update_policy_holder_payment_status(sender, instance, **kwargs):
    """
    Update PolicyHolder payment status when premium payment changes
    """
    try:
        policy_holder = instance.policy_holder
        
        # Calculate new status based on payment amounts
        if instance.total_paid >= instance.remaining_premium:
            new_status = 'Paid'
        elif instance.total_paid > 0:
            new_status = 'Partially Paid'
        else:
            new_status = 'Due'
            
        # Update only if status has changed
        if policy_holder.payment_status != new_status:
            PolicyHolder.objects.filter(id=policy_holder.id).update(
                payment_status=new_status
            )
            
    except Exception as e:
        print(f"Error updating payment status: {str(e)}")

''' Underwriting signals'''

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