from django.dispatch import receiver
from insurance.models import PremiumPayment, AgentReport, PolicyHolder
from django.db.models.signals import post_save
from django.db import transaction
from decimal import Decimal
from django.utils import timezone

@receiver(post_save, sender=PremiumPayment)
def update_agent_report_and_commission(sender, instance, created, **kwargs):
    """Update agent report and commission when a premium payment is made"""
    agent = instance.policy_holder.agent
    if not agent:
        return

    try:
        with transaction.atomic():
            report_date = instance.next_payment_date or timezone.now().date()

            # Get or create monthly report
            report, _ = AgentReport.objects.get_or_create(
                agent=agent,
                branch=agent.branch,
                report_date=report_date.replace(day=1),
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

            # Always calculate & add commission
            commission = (instance.interval_payment * agent.commission_rate / 100)

            report.total_premium += instance.interval_payment
            report.commission_earned += commission

            agent.total_premium_collected += instance.interval_payment
            agent.save()

            # Placeholder target logic
            if hasattr(agent, 'monthly_target') and agent.monthly_target > 0:
                report.target_achievement = (report.total_premium / agent.monthly_target) * 100

            # Placeholder renewal logic
            total_policies = PolicyHolder.objects.filter(agent=agent).count()
            renewed_policies = PolicyHolder.objects.filter(
                agent=agent,
                status='ACTIVE',
                maturity_date__gte=report_date  
            ).count()

            if total_policies > 0:
                report.renewal_rate = (renewed_policies / total_policies) * 100

            report.save()

            print(f"✅ Commission of {commission} credited to agent {agent}.")

    except Exception as e:
        print(f"💥 Error in update_agent_report_and_commission signal: {str(e)}")


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
