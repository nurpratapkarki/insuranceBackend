import sys
from django.apps import AppConfig
from django.db import transaction
from django.utils import timezone

class InsuranceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'insurance'
    
    def ready(self):
        # Skip during migrations, tests, etc.
        if 'runserver' not in sys.argv and 'accrue_interest' not in sys.argv:
            return
        
        # Add a custom command line argument to trigger interest accrual
        if 'accrue_interest' in sys.argv:
            self.accrue_daily_interest()
    
    def accrue_daily_interest(self):
        """Accrue interest on all active loans"""
        from insurance.models import Loan  # Import here to avoid app registry issues
        
        today = timezone.now().date()
        active_loans = Loan.objects.filter(loan_status="Active")
        
        updated_count = 0
        error_count = 0
        
        with transaction.atomic():
            for loan in active_loans:
                try:
                    loan.accrue_interest()
                    updated_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Error processing loan {loan.id}: {str(e)}")
        
        print(f"Interest accrual complete. Updated: {updated_count}, Errors: {error_count}")