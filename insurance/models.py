from datetime import date
from decimal import Decimal
import re
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save  
from typing import Dict, Union
from django.dispatch import receiver
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum
from django.core.exceptions import ValidationError
from insurance.constant import DOCUMENT_TYPES, EMPLOYEE_STATUS_CHOICES, EXE_FREQ_CHOICE, GENDER_CHOICES, PAYMENT_CHOICES, POLICY_TYPES, PROCESSING_STATUS_CHOICES, PROVINCE_CHOICES, RISK_CHOICES, STATUS_CHOICES
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.html import format_html # Import format_html for admin display

# Define Fine Rate (as a percentage)
# Consider moving this to settings.py if it needs to be globally configurable
PREMIUM_FINE_RATE = Decimal('0.02') # Example: 2%

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "superadmin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('branch', 'Branch Admin'),
        ('agent', 'Sales Agent'),
        ('customer', 'Customer'),
    ]
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Male", blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='branch_users')
    agent = models.OneToOneField('SalesAgent', on_delete=models.SET_NULL, null=True, blank=True, related_name='agent_user')
    
    # Fix reverse relationship clash
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='insurance_user_set',
        related_query_name='insurance_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='insurance_user_set',
        related_query_name='insurance_user',
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

#ocupation Model

class Occupation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    risk_category = models.CharField(
        max_length=50,
        choices=[
            ("Low", "Low Risk"),
            ("Moderate", "Moderate Risk"),
            ("High", "High Risk"),
        ],
        default="Moderate",
    )

    def __str__(self):
        return self.name
    
#MortalityRate Model
class MortalityRate(models.Model):
    age_group_start = models.PositiveIntegerField(null=True, blank=True)
    age_group_end = models.PositiveIntegerField(null=True, blank=True)
    rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, null=True, blank=True
    )

    class Meta:
        unique_together = ("age_group_start", "age_group_end")

    def __str__(self):
        return f"{self.age_group_start}-{self.age_group_end}: {self.rate}%"

#Company Model
class Company(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    company_code = models.IntegerField(unique=True, default=1)
    address = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="company", null=True, blank=True)
    email = models.EmailField(max_length=255)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

#Branch Model
class Branch(models.Model):
    name = models.CharField(max_length=255)
    branch_code = models.IntegerField(unique=True, default=1)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='branch_user', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="branches", default=1
    )

    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.name} ({self.branch_code})"

#InsurancePolicy Model

class InsurancePolicy(models.Model):
    name = models.CharField(max_length=200)
    policy_code = models.CharField(max_length=50, unique=True)
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPES, default="Term")
    base_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    min_sum_assured = models.DecimalField(
        max_digits=12, decimal_places=2, default=500.00
    )
    max_sum_assured = models.DecimalField(
        max_digits=12, decimal_places=2, default=10000.00
    )
    include_adb = models.BooleanField(default=False)
    include_ptd = models.BooleanField(default=False)
    adb_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )  # ADB charge %
    ptd_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )  # PTD charge %
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # --- Fields for Maturity Calculation (Stored as Decimals) ---
    guaranteed_interest_rate = models.DecimalField(
        max_digits=7, decimal_places=4, default=0.0000, # Allow slightly more digits for precision e.g. 0.0450
        null=True, blank=True,
        help_text="Guaranteed annual interest rate (e.g., 0.04 for 4%)."
    )
    terminal_bonus_rate = models.DecimalField(
        max_digits=7, decimal_places=4, default=0.0000,
        null=True, blank=True,
        help_text="Terminal bonus rate as a percentage of Sum Assured (e.g., 0.10 for 10%)."
    )
    # --- End of stored fields ---
    
    # --- Properties for Percentage Display/Input ---
    @property
    def guaranteed_interest_rate_percent(self):
        """Returns the guaranteed interest rate as a percentage."""
        if self.guaranteed_interest_rate is not None:
            return (self.guaranteed_interest_rate * 100).quantize(Decimal('0.01'))
        return None

    @guaranteed_interest_rate_percent.setter
    def guaranteed_interest_rate_percent(self, value):
        """Sets the guaranteed interest rate from a percentage."""
        if value is not None:
            try:
                self.guaranteed_interest_rate = (Decimal(str(value)) / 100).quantize(Decimal('0.0001'))
            except (TypeError, ValueError, InvalidOperation):
                # Handle potential errors if input is not a valid number
                self.guaranteed_interest_rate = None 
        else:
            self.guaranteed_interest_rate = None

    @property
    def terminal_bonus_rate_percent(self):
        """Returns the terminal bonus rate as a percentage."""
        if self.terminal_bonus_rate is not None:
            return (self.terminal_bonus_rate * 100).quantize(Decimal('0.01'))
        return None

    @terminal_bonus_rate_percent.setter
    def terminal_bonus_rate_percent(self, value):
        """Sets the terminal bonus rate from a percentage."""
        if value is not None:
            try:
                self.terminal_bonus_rate = (Decimal(str(value)) / 100).quantize(Decimal('0.0001'))
            except (TypeError, ValueError, InvalidOperation):
                self.terminal_bonus_rate = None
        else:
            self.terminal_bonus_rate = None
    # --- End of properties ---

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Insurance Policy"
        verbose_name_plural = "Insurance Policies"

    def clean(self):
        super().clean()
        if self.policy_type == "Term" and self.base_multiplier != 1.0:
            raise ValidationError(
                "Base multiplier for Term insurance must always be 1.0."
            )
    
    # We don't need to override save(), the properties handle the conversion before save.

#Guanteed Surrender Value Model
class GSVRate(models.Model):
    policy = models.ForeignKey(
        "InsurancePolicy", on_delete=models.CASCADE, related_name="gsv_rates"
    )
    min_year = models.PositiveIntegerField(help_text="Minimum year of the range.")
    max_year = models.PositiveIntegerField(help_text="Maximum year of the range.")
    rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="GSV rate as a percentage."
    )
   
    @classmethod
    def calculate_gsv(cls, premium_payment):
        """Calculate Guaranteed Surrender Value (GSV) based on a PremiumPayment."""
        try:
            policy_holder = premium_payment.policy_holder
            duration_years = (date.today() - policy_holder.start_date).days // 365
            gsv_rate = policy_holder.policy.gsv_rates.filter(
                min_year__lte=duration_years, max_year__gte=duration_years
            ).first()

            if not gsv_rate:
                return Decimal("0.00")  # No GSV defined for current duration

            paid_premium = max(premium_payment.total_paid - premium_payment.annual_premium, Decimal("0.00"))
            return (paid_premium * gsv_rate.rate / Decimal(100)).quantize(Decimal("1.00"))
        except Exception as e:
            raise ValidationError(f"Error calculating GSV: {e}")

    def clean(self):
        """Ensure the year range is valid and does not overlap with other GSV ranges."""
        if self.min_year >= self.max_year:
            raise ValidationError("Minimum year must be less than maximum year.")

        # Get all existing ranges for the policy
        existing_ranges = GSVRate.objects.filter(policy=self.policy).exclude(
            pk=self.pk
        )  # Exclude the current instance

        # Check for overlaps using strict inequality for ranges
        overlapping = existing_ranges.filter(
            models.Q(
                # New range starts strictly before existing range ends
                min_year__lt=self.max_year,
                # AND existing range ends strictly after new range starts
                max_year__gt=self.min_year,
            )
        )

        if overlapping.exists():
            raise ValidationError("GSV year ranges cannot overlap for the same policy.")

    def __str__(self):
        return f"GSV Rate {self.rate}% for {self.min_year}-{self.max_year} years"
    

#Special Surrender Value Model

class SSVConfig(models.Model):
    policy = models.ForeignKey(
        "InsurancePolicy", on_delete=models.CASCADE, related_name="ssv_configs"
    )
    min_year = models.PositiveIntegerField(help_text="Minimum year of the range.")
    max_year = models.PositiveIntegerField(help_text="Maximum year of the range.")
    ssv_factor = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="SSV factor as a percentage."
    )
    eligibility_years = models.PositiveIntegerField(
        default=5, help_text="Years of premium payment required for SSV eligibility."
    )
    custom_condition = models.TextField(
        blank=True, help_text="Optional custom condition for SSV."
    )

    # Calculate Surrender Value
    @classmethod
    def calculate_ssv(cls, premium_payment):
        """Calculate Special Surrender Value (SSV) based on PremiumPayment."""
        try:
            policy_holder = premium_payment.policy_holder

            if policy_holder.policy.policy_type != "Endownment":
                return Decimal("0.00")  # SSV only applies to endowment policies

            duration_years = (date.today() - policy_holder.start_date).days // 365
            premiums_paid = policy_holder.premium_payments.count()

            # Get applicable SSV configuration
            applicable_range = policy_holder.policy.ssv_configs.filter(
                min_year__lte=duration_years, max_year__gte=duration_years
            ).first()

            if (
                not applicable_range
                or premiums_paid < applicable_range.eligibility_years
            ):
                return Decimal("0.00")

            # Total Bonuses
            total_bonuses = policy_holder.bonuses.aggregate(
                total=Sum("accrued_amount")
            )["total"] or Decimal("0.00")

            # Calculate SSV
            premium_component = premium_payment.total_paid * (
                applicable_range.ssv_factor / Decimal(100)
            )
            ssv = premium_component + total_bonuses

            return ssv.quantize(Decimal("1.00"))

        except Exception as e:
            raise ValidationError(f"Error calculating SSV: {e}")

    def clean(self):
        """Ensure the year range is valid and does not overlap with other SSV ranges."""
        if self.min_year >= self.max_year:
            raise ValidationError("Minimum year must be less than maximum year.")

        overlapping = SSVConfig.objects.filter(
            policy=self.policy, min_year__lte=self.max_year, max_year__gte=self.min_year
        ).exclude(pk=self.pk)  # Exclude the current instance

        if overlapping.exists():
            raise ValidationError("SSV year ranges cannot overlap for the same policy.")
            
    def __str__(self):
        return (
            f"SSV Factor {self.ssv_factor}% for {self.min_year}-{self.max_year} years"
        )
#Agent Application Model
class AgentApplication(models.Model):
    id = models.BigAutoField(primary_key=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="agent_applications", default=1
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)
    grand_father_name = models.CharField(max_length=200, null=True, blank=True)
    grand_mother_name = models.CharField(max_length=200, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Male")
    email = models.EmailField(max_length=200, unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    resume = models.FileField(upload_to="agent_application", null=True, blank=True)
    citizenship_front = models.ImageField(
        upload_to="agent_application", null=True, blank=True
    )
    citizenship_back = models.ImageField(
        upload_to="agent_application", null=True, blank=True
    )
    license_front = models.ImageField(
        upload_to="agent_application", null=True, blank=True
    )
    license_back = models.ImageField(
        upload_to="agent_application", null=True, blank=True
    )
    pp_photo = models.ImageField(upload_to="agent_application", null=True, blank=True)
    license_number = models.CharField(max_length=50, null=True, blank=True)
    license_issue_date = models.DateField(null=True, blank=True)
    license_expiry_date = models.DateField(null=True, blank=True)
    license_type = models.CharField(max_length=50, null=True, blank=True)
    license_issue_district = models.CharField(max_length=50, null=True, blank=True)
    license_issue_zone = models.CharField(max_length=50, null=True, blank=True)
    license_issue_province = models.CharField(max_length=50, null=True, blank=True)
    license_issue_country = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    def clean(self):
        """Validate the phone number format."""
        errors = {}  # Initialize the errors dictionary
        phone_pattern = r'^\d{10}$'
        if self.phone_number and not re.match(phone_pattern, self.phone_number):
            errors["phone_number"] = "Phone number must be exactly 10 digits."

        if errors:
            raise ValidationError(errors)
    class Meta:
        verbose_name = "Agent Application"
        verbose_name_plural = "Agent Applications"
        indexes = [
            models.Index(fields=["branch"]),
            models.Index(fields=["status"]),
        ]


#Agent Model
class SalesAgent(models.Model):
    id = models.BigAutoField(primary_key=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="sales_agents", default=1
    )
    application = models.OneToOneField(
        AgentApplication,
        on_delete=models.SET_NULL,
        related_name="sales_agent",
        null=True,
        blank=True,
    )

    agent_code = models.CharField(max_length=50, unique=True, default=1)
    is_active = models.BooleanField(default=True)
    joining_date = models.DateField(default=date.today)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_policies_sold = models.IntegerField(default=0)
    total_premium_collected = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    last_policy_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    termination_reason = models.CharField(max_length=200, null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=EMPLOYEE_STATUS_CHOICES, default="ACTIVE"
    )

    def __str__(self):
        if self.application:
            return f"{self.application.first_name} {self.application.last_name} ({self.agent_code})"
        return self.agent_code

    def get_full_name(self):
        if self.application:
            return f"{self.application.first_name} {self.application.last_name}"
        return None

    class Meta:
        verbose_name = "Sales Agent"
        verbose_name_plural = "Sales Agents"
        indexes = [
            models.Index(fields=["branch"]),
            models.Index(fields=["total_policies_sold"]),
            models.Index(fields=["status"]),
        ]
#Duration Factor Model

class DurationFactor(models.Model):
    min_duration = models.PositiveIntegerField(help_text="Minimum duration in years")
    max_duration = models.PositiveIntegerField(help_text="Maximum duration in years")
    factor = models.DecimalField(max_digits=5, decimal_places=2)
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPES)

    class Meta:
        unique_together = ["min_duration", "max_duration", "policy_type"]
        ordering = ["min_duration"]

    def clean(self):
        if self.min_duration >= self.max_duration:
            raise ValidationError("Minimum duration must be less than maximum duration")

        overlapping = DurationFactor.objects.filter(
            policy_type=self.policy_type,
            min_duration__lte=self.max_duration,
            max_duration__gte=self.min_duration,
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(
                "Duration ranges cannot overlap for the same policy type"
            )

    def __str__(self):
        return f"{self.policy_type} ({self.min_duration}-{self.max_duration} years): {self.factor}x"


#Customer Model
class Customer(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    # Change related_name to resolve the clash
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    email = models.EmailField(max_length=200, unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=200)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        creating = self.pk is None and self.user is None
        
        # Ensure email exists before proceeding
        if not self.email:
            raise ValueError("Customer must have an email address to create a user.")

        super().save(*args, **kwargs)
        
        if creating:
            # Generate username from email prefix
            username_prefix = self.email.split('@')[0]
            # Ensure username is unique. If not, append customer ID.
            # This is a simple approach; more robust uniqueness might be needed.
            username = username_prefix
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_prefix}_{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username, # Use generated username
                email=self.email,
                password=None, # No password set by default
                first_name=self.first_name,
                last_name=self.last_name,
                user_type='customer',
                phone=self.phone_number,
                address=self.address
            )
            
            self.user = user
            self.save(update_fields=['user']) # Save the user reference back to customer
    
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=["email"]),
        ]
#Kyc Model
class KYC(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="kyc")
    document_type = models.CharField(max_length=111, choices=DOCUMENT_TYPES, blank=True, null=True)
    document_number = models.CharField(max_length=50, default=1)
    document_front = models.ImageField(upload_to="customer_kyc/")
    document_back = models.ImageField(upload_to="customer_kyc/")
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    pan_front = models.ImageField(upload_to="customer_kyc/", null=True, blank=True)
    pan_back = models.ImageField(upload_to="customer_kyc/", null=True, blank=True)
    pp_photo = models.ImageField(upload_to="customer_kyc/")

    # Address
    province = models.CharField(max_length=255, choices=PROVINCE_CHOICES, default="Karnali")
    district = models.CharField(max_length=255)
    municipality = models.CharField(max_length=255)
    ward = models.CharField(max_length=255)
    nearest_hospital = models.CharField(max_length=255, blank=True, null=True)
    natural_hazard_exposure = models.CharField(max_length=50, choices=RISK_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"KYC for {self.customer.first_name} {self.customer.last_name}"
    class Meta:
        verbose_name = "KYC"
        verbose_name_plural = "KYC"
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["status"]),
        ]
#Policy Holder Model

class PolicyHolder(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="policy_holders", default=1
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="policies", null=True)
    policy_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    agent = models.ForeignKey(
        SalesAgent, on_delete=models.CASCADE, null=True, blank=True
    )
    policy = models.ForeignKey(
        InsurancePolicy,
        related_name="policy_holders",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    duration_years = models.PositiveIntegerField(default=1)
    sum_assured = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
 
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(editable=False, null=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
    nominee_name = models.CharField(max_length=200, null=True, blank=True)
    nominee_document_type = models.CharField(
        max_length=111, blank=True, null=True, choices=DOCUMENT_TYPES
    )
    nominee_document_number = models.PositiveIntegerField(null=True, blank=True)
    nominee_document_front = models.ImageField(upload_to="policyHolder")
    nominee_document_back = models.ImageField(upload_to="policyHolder")
    nominee_pp_photo = models.ImageField(upload_to="policyHolder")
    nominee_relation = models.CharField(max_length=255)
    include_adb = models.BooleanField(default=False)
    include_ptd = models.BooleanField(default=False)
    health_history = models.CharField(max_length=500, null=True, blank=True)
    habits = models.CharField(max_length=500, null=True, blank=True)
    exercise_frequency = models.CharField(
        max_length=50, choices=EXE_FREQ_CHOICE, blank=True, null=True
    )
    alcoholic = models.BooleanField(default=False)
    smoker = models.BooleanField(default=False)
    past_medical_report = models.FileField(
        upload_to="policy_holders", null=True, blank=True
    )
    family_medical_history = models.TextField(null=True, blank=True)
    recent_medical_reports = models.FileField(
        upload_to="policy_holders", blank=True, null=True
    )
    yearly_income = models.CharField(max_length=455, default=500000)
    occupation = models.ForeignKey(
        Occupation, on_delete=models.SET_NULL, null=True, blank=True
    )
    assets_details = models.TextField(max_length=5000, null=True, blank=True)
    payment_interval = models.CharField(
        max_length=20,
        choices=[
            ("Single", "Single"),
            ("quarterly", "Quarterly"),
            ("semi_annual", "Semi-Annual"),
            ("annual", "Annual"),
        ],
        default="annual",
    )
    risk_category = models.CharField(
        max_length=50,
        choices=[
            ("Low", "Low Risk"),
            ("Moderate", "Moderate Risk"),
            ("High", "High Risk"),
        ],
        default="Moderate",
        blank=True,
        help_text="Risk category assigned based on underwriting.",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    payment_status = models.CharField(
        max_length=50, choices=PROCESSING_STATUS_CHOICES, default="Due"
    )
    start_date = models.DateField(default=date.today)
    maturity_date = models.DateField(null=True, blank=True)

    def clean(self):
        """Validate the phone number format."""
        errors = {}
        phone_pattern = r'^\d{10}$'
        if self.phone_number and not re.match(phone_pattern, self.phone_number):
            errors["phone_number"] = "Phone number must be exactly 10 digits."

        if self.sum_assured:
            if self.sum_assured < self.policy.min_sum_assured:
                errors["sum_assured"] = (
                    f"Sum assured must be at least {self.policy.min_sum_assured}."
                )
            elif self.sum_assured > self.policy.max_sum_assured:
                errors["sum_assured"] = (
                    f"Sum assured cannot exceed {self.policy.max_sum_assured}."
                )
                
        if self.date_of_birth:
            age = self.calculate_age()
            if age < 18 or age > 60:
                errors["date_of_birth"] = (
                    f"Age must be between 18 and 60. Current age: {age}."
                )
                
        if errors:
            raise ValidationError(errors)

    def calculate_age(self):
        """Calculate age based on date of birth"""
        today = now().date()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    def calculate_maturity_date(self):
        """Calculate maturity date based on start date and duration"""
        if self.start_date and self.duration_years:
            return self.start_date.replace(
                year=self.start_date.year + self.duration_years
            )
        return None

    def generate_policy_number(self):
        """Generate a unique policy number based on company, branch, and policy codes."""
        if not self.company or not self.branch or not self.policy:
            return None

        try:
            # Format: CompanyCode + BranchCode + PolicyCode + Sequence
            prefix = f"{self.company.company_code}{self.branch.branch_code}{self.policy.policy_code}"
            
            # Find the latest policy number with the same prefix
            latest_policy = PolicyHolder.objects.filter(
                policy_number__startswith=prefix
            ).order_by('-policy_number').first()
            
            if latest_policy and latest_policy.policy_number:
                # Extract the sequence number and increment it
                sequence_str = latest_policy.policy_number[len(prefix):]
                try:
                    sequence = int(sequence_str) + 1
                except ValueError:
                    sequence = 1
            else:
                sequence = 1
                
            return f"{prefix}{str(sequence).zfill(4)}"
        except Exception as e:
            raise ValueError(f"Error generating policy number: {e}")
        
    def validate_kyc(self):
        """Validate KYC status before issuing a policy."""
        errors = {}
        if not self.customer:
            errors["customer"] = "Customer must be provided."
        elif not hasattr(self.customer, "kyc"):
            errors["customer"] = "Customer KYC must be completed before issuing a policy."
        elif self.customer.kyc.status != "Approved":
            errors["customer"] = "Customer KYC is not approved."
        elif self.customer.kyc.status == "Pending":
            errors["customer"] = "Customer KYC is still pending approval."
        if errors:
            raise ValidationError(errors)

    def calculate_actual_maturity_value(self) -> Decimal:
        """Calculates the *actual* maturity value based on policy data and accrued bonuses."""
        try:
            if self.status != 'Active' and self.status != 'Matured': # Or whatever status indicates maturity eligibility
                # Maybe return 0 or raise an error if not mature?
                print(f"Policy {self.policy_number} is not yet mature or active.")
                return Decimal("0.00")

            policy = self.policy
            sum_assured = self.sum_assured or Decimal('0.00')
            policy_term = Decimal(str(self.duration_years)) if self.duration_years else Decimal('0')
            
            # Get the associated premium payment record (assuming one exists)
            # We need annual_premium from it for guaranteed additions calculation
            premium_payment = self.premium_payments.first() # Get the latest or first?
            annual_premium = premium_payment.annual_premium if premium_payment else Decimal('0.00')

            # --- Calculate Components --- 

            # 1. Guaranteed Additions (Compound Interest on Annual Premium)
            guaranteed_rate = policy.guaranteed_interest_rate if policy.guaranteed_interest_rate is not None else Decimal('0.0000')
            guaranteed_additions_future_value = Decimal('0.00')
            if guaranteed_rate > 0 and annual_premium > 0 and policy_term > 0:
                # Future Value of an Ordinary Annuity: P * [((1 + r)^n - 1) / r]
                try:
                    future_value_factor = ((Decimal(1) + guaranteed_rate)**policy_term - Decimal(1)) / guaranteed_rate
                    guaranteed_additions_future_value = annual_premium * future_value_factor
                except InvalidOperation:
                     # Handle potential calculation errors (e.g., overflow if term is huge)
                     print(f"Error calculating future value factor for Policy {self.policy_number}")
                     guaranteed_additions_future_value = annual_premium * policy_term # Fallback to total premium?
            else:
                # If no rate/term/premium, future value is just total premiums paid
                 guaranteed_additions_future_value = annual_premium * policy_term

            # 2. Actual Accrued Bonuses (Sum from related Bonus objects)
            # Ensure bonuses are linked to PolicyHolder now
            total_actual_bonus = self.bonuses.aggregate(total=Sum('accrued_amount'))['total'] or Decimal('0.00')

            # 3. Terminal Bonus Component
            terminal_rate = policy.terminal_bonus_rate if policy.terminal_bonus_rate is not None else Decimal('0.0000')
            terminal_bonus_component = sum_assured * terminal_rate

            # --- Total Actual Maturity Value --- 
            # Sum Assured + Future Value of Guaranteed Additions + Actual Accrued Bonuses + Terminal Bonus
            maturity_value = (
                sum_assured + 
                guaranteed_additions_future_value + # Total value (premium principal + interest)
                total_actual_bonus + 
                terminal_bonus_component
            )
            
            # Consider product variations as noted in the estimated calculation

            return maturity_value.quantize(Decimal("1.00"))

        except Exception as e:
            import traceback
            print(f"Error calculating actual maturity value for PolicyHolder {self.id}: {e}")
            traceback.print_exc() # Print detailed traceback
            return Decimal("0.00")

    def save(self, *args, **kwargs):
        """Override save method to handle automatic field updates"""
        # Calculate age if date of birth is provided
        if self.date_of_birth:
            self.age = self.calculate_age()

        # Generate policy number if status is Active and number doesn't exist
        if self.status == "Active" and not self.policy_number:
            self.policy_number = self.generate_policy_number()

        # Set maturity date if not already set
        if not self.maturity_date:
            self.maturity_date = self.calculate_maturity_date()

        # Run full validation
        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the policy holder"""
        if self.customer:
            customer_name = f"{self.customer.first_name} {self.customer.last_name}"
        else:
            customer_name = "No Customer"
            
        policy_num = self.policy_number if self.policy_number else "Pending"
        return f"{customer_name} ({policy_num})"

    class Meta:
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["policy"]),
        ]
#BonusRate Model
class BonusRate(models.Model):
    year = models.PositiveIntegerField(
        default=date.today().year,  
        help_text="Year the bonus rate applies to",
    )
    policy = models.ForeignKey(
        "InsurancePolicy", on_delete=models.CASCADE, related_name="bonus_rates"
    )
    min_year = models.PositiveIntegerField(
        help_text="Minimum policy duration in years for this rate", default=1
    )
    max_year = models.PositiveIntegerField(
        help_text="Maximum policy duration in years for this rate", default=9
    )
    bonus_per_thousand = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Bonus amount per 1000 of sum assured",
        default=0.00,
    )

    class Meta:
        # Updated unique_together constraint
        unique_together = ['policy', 'year', 'min_year', 'max_year'] 
        ordering = ["policy", "year", "min_year"] # Updated ordering

    def clean(self):
        """Ensure the year range is valid and does not overlap (or touch boundaries) with other ranges for the same policy and year."""
        if self.min_year is None or self.max_year is None:
             raise ValidationError("Minimum and Maximum year duration must be set.")
        # Allow min_year == max_year for single-year duration, but not min > max
        if self.min_year > self.max_year:
            raise ValidationError({"max_year": "Maximum year must be greater than or equal to minimum year."}) 

        # Check for overlapping ranges for the SAME policy and SAME year
        # Filter out potential None values if policy or year are not set yet (though they should be required)
        if self.policy is not None and self.year is not None:
            overlapping_ranges = BonusRate.objects.filter(
                policy=self.policy,
                year=self.year,
                min_year__lte=self.max_year, # Existing min <= New max
                max_year__gte=self.min_year  # Existing max >= New min
            ).exclude(pk=self.pk) # Exclude self if editing

            if overlapping_ranges.exists():
                overlaps = ", ".join([f"{o.min_year}-{o.max_year}" for o in overlapping_ranges])
                raise ValidationError(
                     f"The duration range {self.min_year}-{self.max_year} overlaps with existing range(s) [{overlaps}] "
                     f"for this policy in year {self.year}."
                 )
        super().clean() # Call parent clean method

    def __str__(self):
        # Correctly access policy name and type through the relationship
        policy_name = self.policy.name if self.policy else "No Policy"
        return f"{policy_name} ({self.year}): {self.min_year}-{self.max_year} years -> {self.bonus_per_thousand} per 1000"

    @classmethod
    def get_bonus_rate(cls, policy, duration):
        """Fetch the correct bonus rate based on policy and duration for the latest applicable year."""
        # Find the latest year for which a rate exists for this policy and duration
        latest_rate = cls.objects.filter(
            policy=policy, 
            min_year__lte=duration, 
            max_year__gte=duration
        ).order_by('-year').first()
        return latest_rate # Return the whole object or just the rate? Returning object is more flexible

#Bonus Model

class Bonus(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="bonuses"
    )
    policy_holder = models.ForeignKey(
        PolicyHolder, on_delete=models.CASCADE, related_name="bonuses"
    )
    bonus_type = models.CharField(
        max_length=20,
        choices=[("SI", "Simple Interest"), ("CI", "Compound Interest")],
        default="SI",
    )
    accrued_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    start_date = models.DateField(help_text="Start date for bonus accrual.")

    def calculate_bonus(self):
        """Calculate yearly bonus based on policy type, duration, and sum assured."""
        try:
            policy = self.policy_holder.policy
            duration = self.policy_holder.duration_years
            sum_assured = self.policy_holder.sum_assured
            # Fetch applicable bonus rate
            bonus_rate_obj = BonusRate.get_bonus_rate(policy, duration)

            if not bonus_rate_obj:
            
                return Decimal(0)  # No bonus if rate is not defined

            bonus_per_1000 = Decimal(str(bonus_rate_obj.bonus_per_thousand))
            sum_assured = Decimal(str(sum_assured))

           

            total_bonus = (sum_assured / Decimal(1000)) * bonus_per_1000

           
            return total_bonus.quantize(Decimal("1.00"))

        except Exception as e:
           
            raise ValidationError(f"Error calculating bonus: {e}")

    def save(self, *args, **kwargs):
        """Override save to calculate bonus before saving."""
        self.accrued_amount = self.calculate_bonus()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bonus for {self.policy_holder} on {self.start_date}"
    
    
#ClaimRequest Model

class ClaimRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    policy_holder = models.ForeignKey(PolicyHolder, on_delete=models.CASCADE, related_name="claims")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="claims")
    claim_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    reason = models.CharField(max_length=100)
    other_reason = models.TextField(blank=True, null=True)
    documents = models.FileField(upload_to="claims/", blank=True, null=True)  # Simplified doc upload
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def calculate_claim_amount(self):
        """Calculate the base claim amount, defaulting to 100% of Sum Assured."""
        if self.policy_holder and self.policy_holder.sum_assured:
            # Changed from 0.60 to 1.00 (or just return the sum_assured directly)
            return self.policy_holder.sum_assured 
        return Decimal("0")

    def save(self, *args, **kwargs):
        # If claim_amount is not provided (or is 0), calculate the default
        if not self.claim_amount or self.claim_amount == Decimal('0'): 
            self.claim_amount = self.calculate_claim_amount()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Claim by {self.policy_holder} on {self.claim_date}"
    class Meta:
        verbose_name = "Claim Request"
        verbose_name_plural = "Claim Requests"
        indexes = [
            models.Index(fields=["policy_holder"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["status"]),
        ]

#ClaimProcessing Model
class ClaimProcessing(models.Model):
    PROCESSING_STATUS_CHOICES = [
        ("Processing", "Processing"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    claim_request = models.OneToOneField(ClaimRequest, on_delete=models.CASCADE, related_name="processing")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default="Processing")
    remarks = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(auto_now=True)

    def finalize_claim(self):
        if self.processing_status == "Approved":
            from .models import PaymentProcessing
            PaymentProcessing.objects.create(
                claim_request=self.claim_request,
                branch=self.branch,
                company=self.company,
                processing_status="Completed",
            )
            self.claim_request.status = "Approved"
            self.claim_request.save()
        elif self.processing_status == "Rejected":
            self.claim_request.status = "Rejected"
            self.claim_request.save()

    def __str__(self):
        return f"Processing for {self.claim_request}"
    class Meta:
        verbose_name = "Claim Processing"
        verbose_name_plural = "Claim Processings"
        indexes = [
            models.Index(fields=["claim_request"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["company"]),
            models.Index(fields=["processing_status"]),
        ]
#PaymentProcessing Model

class PaymentProcessing(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ]

    claim_request = models.OneToOneField(
        ClaimRequest, on_delete=models.CASCADE, related_name="payment"
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    processing_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Pending"
    )
    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)

    def calculate_payout(self):
        """
        Calculate the claim payout amount.
        Base Payout = Sum Assured + Actual Accrued Bonuses - Total Outstanding Loan.
        NOTE: Rider amounts (ADB/PTD) are NOT automatically added here and need specific logic 
              based on claim reason if applicable.
        """
        try:
            claim = self.claim_request
            ph = claim.policy_holder
            policy = ph.policy

            # Base amount: Sum Assured
            payout_base = ph.sum_assured or Decimal('0.00')

            # --- START: Commented-out Rider Logic (Needs Refinement) --- 
            # The logic below needs refinement based on specific claim reason and rider rules.
            # It currently adds the full sum assured unconditionally if rider is included.
            # if ph.include_adb: 
            #     print(f"DEBUG: Adding ADB amount ({ph.sum_assured}) for claim {claim.id}")
            #     payout_base += ph.sum_assured or Decimal('0.00')
            # if ph.include_ptd:
            #     print(f"DEBUG: Adding PTD amount ({ph.sum_assured}) for claim {claim.id}")
            #     payout_base += ph.sum_assured or Decimal('0.00')
            # --- END: Commented-out Rider Logic --- 

            # Add Actual Accrued Bonuses (Sum from related Bonus objects)
            total_actual_bonus = ph.bonuses.aggregate(total=Sum('accrued_amount'))['total'] or Decimal('0.00')

            # Calculate Total Outstanding Loan Amount (Principal + Interest)
            total_outstanding_loan = Decimal('0.00')
            active_loans = ph.loans.filter(loan_status='Active')
            for loan in active_loans:
                total_outstanding_loan += (loan.remaining_balance + loan.accrued_interest)

            # Final Payout Calculation (Current Active Logic)
            payout = payout_base + total_actual_bonus - total_outstanding_loan
            
            # Ensure payout is not negative
            payout = max(payout, Decimal('0.00')) 

            return payout.quantize(Decimal("1.00"))

        except Exception as e:
            import traceback
            print(f"Error calculating payout for Claim Request {claim.id if claim else 'N/A'}: {e}")
            traceback.print_exc()
            return Decimal("0.00")

    def save(self, *args, **kwargs):
        # Calculate payout only if status is being set to Completed and amount_paid is not set yet
        # Or perhaps recalculate whenever saved? Simpler: Recalculate on save if amount is 0.
        if self.amount_paid == Decimal('0.00'): # Recalculate if 0
            self.amount_paid = self.calculate_payout()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payout for {self.claim_request.policy_holder}"

    class Meta:
        verbose_name = "Payment Processing"
        verbose_name_plural = "Payment Processings"
        indexes = [
            models.Index(fields=["claim_request"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["company"]),
            models.Index(fields=["processing_status"]),
        ]


# Underwriting Process Or report
class Underwriting(models.Model):
    policy_holder = models.OneToOneField(
        "PolicyHolder", on_delete=models.CASCADE, related_name="underwriting"
    )
    risk_assessment_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Calculated risk score (0-100).",
    )
    risk_category = models.CharField(
        max_length=50,
        choices=[
            ("Low", "Low Risk"),
            ("Moderate", "Moderate Risk"),
            ("High", "High Risk"),
        ],
        default="Moderate",
    )
    manual_override = models.BooleanField(
        default=False, help_text="Enable to manually update risk scores."
    )
    remarks = models.TextField(
        null=True, blank=True, help_text="Additional remarks about underwriting."
    )
    last_updated_by = models.CharField(
        max_length=50,
        choices=[("System", "System"), ("Admin", "Admin")],
        default="System",
    )
    last_updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Only calculate risk if manual override is disabled
        if not self.manual_override:
            self.calculate_risk()
            self.last_updated_by = "System"
        else:
            self.last_updated_by = "Admin"
        super().save(*args, **kwargs)

    def calculate_risk(self):
        """Automatically calculate the risk score based on policyholder data."""
        try:
            age = self.policy_holder.age
            occupation_risk = 10  # Default risk value if occupation is None
            if self.policy_holder.occupation:
                occupation_risk = {"Low": 10, "Moderate": 20, "High": 30}.get(
                    self.policy_holder.occupation.risk_category, 10
                )

            # Age-based risk
            age_risk = 5 if age < 30 else (15 if age <= 50 else 25)

            # Health and lifestyle risks
            health_risk = 0
            if self.policy_holder.smoker:
                health_risk += 20
            if self.policy_holder.alcoholic:
                health_risk += 15

            # Final risk score
            total_risk = age_risk + occupation_risk + health_risk
            self.risk_assessment_score = min(total_risk, 100)
            self.risk_category = self.determine_risk_category()
        except Exception as e:
            raise ValidationError(f"Error calculating risk: {e}")

    def determine_risk_category(self):
        score = self.risk_assessment_score
        return "Low" if score < 40 else "Moderate" if score < 70 else "High"

    def __str__(self):
        return f"Underwriting for {self.policy_holder} ({self.risk_category})"

#PremiumPayment Model
class PremiumPayment(models.Model):
    policy_holder = models.ForeignKey(
        "PolicyHolder", on_delete=models.CASCADE, related_name="premium_payments"
    )
    annual_premium = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    interval_payment = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    total_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    paid_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, 
        help_text="Amount being paid in this transaction."
    )
    next_payment_date = models.DateField(null=True, blank=True)
    # Fine due represents the *accumulated* unpaid fine amount
    fine_due = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, 
        help_text="Accumulated fine amount due."
    )
    total_premium = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    remaining_premium = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    gsv_value = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    ssv_value = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    payment_status = models.CharField(
        max_length=255, choices=PAYMENT_CHOICES, default="Unpaid"
    )

    def clean(self):
        """Add validation for paid_amount."""
        super().clean() # Call parent clean method
        
        # Ensure amounts are Decimal
        paid_amount = Decimal(str(self.paid_amount)) if self.paid_amount is not None else Decimal('0.00')
        interval_payment = Decimal(str(self.interval_payment)) if self.interval_payment is not None else Decimal('0.00')
        fine_due = Decimal(str(self.fine_due)) if self.fine_due is not None else Decimal('0.00')

        # Validate paid_amount against the amount currently due (interval + fine)
        # Allow paying more only if the policy is already fully paid? (Could be complex)
        # Simple approach: Don't allow paying more than interval + fine in one go unless it clears the total remaining.
        amount_due_this_interval = interval_payment + fine_due
        if paid_amount > amount_due_this_interval:
            # Optional: Allow overpayment if it covers the total remaining premium + fine?
            # total_remaining_with_fine = self.remaining_premium + fine_due
            # if paid_amount > total_remaining_with_fine:
            #     raise ValidationError(f"Paid amount ({paid_amount}) cannot exceed the total remaining premium plus fine ({total_remaining_with_fine}).")
            # Simpler validation for now:
             raise ValidationError(f"Paid amount ({paid_amount}) cannot exceed the current interval payment plus fine due ({amount_due_this_interval}).")

    def calculate_premium(self):
        """Calculate total and interval premiums for the policy."""
        try:
            policy = self.policy_holder.policy
            sum_assured = self.policy_holder.sum_assured
            duration_years = self.policy_holder.duration_years
            age = self.policy_holder.age  # Ensure this field exists in PolicyHolder

            if not policy or not sum_assured or not age:
                raise ValidationError(
                    "Policy, Sum Assured, and Age are required for premium calculation."
                )

            # Fetch mortality rate based on age range
            mortality_rate_obj = MortalityRate.objects.filter(
                age_group_start__lte=age, age_group_end__gte=age
            ).first()

            if not mortality_rate_obj:
                return Decimal("0.00"), Decimal("0.00") # Ensure Decimal return

            mortality_rate = Decimal(mortality_rate_obj.rate)

            # Base premium calculation
            base_premium = (sum_assured * mortality_rate) / Decimal(100)

            # Fetch duration factor
            duration_factor_obj = DurationFactor.objects.filter(
                min_duration__lte=duration_years, max_duration__gte=duration_years
            ).first()

            if not duration_factor_obj:
                return Decimal("0.00"), Decimal("0.00") # Ensure Decimal return

            duration_factor = Decimal(
                duration_factor_obj.factor
            )  # Ensure it's a Decimal

            # Adjust premium based on policy type
            if policy.policy_type == "Endownment":
                adjusted_premium = (
                    base_premium * Decimal(policy.base_multiplier) * duration_factor
                )
            elif policy.policy_type == "Term":
                adjusted_premium = base_premium
            else:
                raise ValidationError(f"Unsupported policy type: {policy.policy_type}")

            # Add ADB/PTD charges if applicable
            adb_charge = (
                (sum_assured * Decimal(policy.adb_percentage)) / Decimal(100)
                if policy.include_adb
                else Decimal("0.00")
            )
            ptd_charge = (
                (sum_assured * Decimal(policy.ptd_percentage)) / Decimal(100)
                if policy.include_ptd
                else Decimal("0.00")
            )

            annual_premium = adjusted_premium + adb_charge + ptd_charge

            # Calculate interval payments
            interval_mapping = {
                "quarterly": 4,
                "semi_annual": 2,
                "annual": 1,
                "Single": 1,
            }
            interval_count = interval_mapping.get(
                self.policy_holder.payment_interval, 1
            )
            interval_payment = annual_premium / Decimal(interval_count)

            return annual_premium.quantize(Decimal("1.00")), interval_payment.quantize(
                Decimal("1.00")
            )

        except Exception as e: # Catch generic exceptions too
             print(f"Error calculating premium for PolicyHolder {self.policy_holder_id}: {e}")
             # Consider logging the error properly
             return Decimal("0.00"), Decimal("0.00") # Return default Decimals on error

    def save(self, *args, **kwargs):
        # Ensure amounts are Decimal
        self.paid_amount = Decimal(str(self.paid_amount)) if self.paid_amount is not None else Decimal('0.00')
        self.fine_due = Decimal(str(self.fine_due)) if self.fine_due is not None else Decimal('0.00')

        # Calculate base premiums on first save
        is_new = self.pk is None
        if is_new:
            self.annual_premium, self.interval_payment = self.calculate_premium()
            if self.policy_holder.payment_interval == "Single":
                self.total_premium = self.interval_payment
            else:
                self.total_premium = self.annual_premium * Decimal(str(self.policy_holder.duration_years))
            # Set first payment date if not single payment
            if self.policy_holder.payment_interval != "Single":
                 self.next_payment_date = self.calculate_next_payment_date(self.policy_holder.start_date)

        # --- Fine Calculation (before processing payment) ---
        # Check if payment is late and policy is not already fully paid
        if self.next_payment_date and date.today() > self.next_payment_date and self.payment_status != 'Paid':
            # Calculate fine based on interval payment (only if interval > 0)
            if self.interval_payment > 0:
                calculated_fine = (self.interval_payment * PREMIUM_FINE_RATE).quantize(Decimal('1.00'))
                # Add fine only if it hasn't been added for this overdue period yet?
                # Requires tracking last fine calculation date - complex. Simpler: Add if late.
                self.fine_due += calculated_fine 
                print(f"Applied fine of {calculated_fine} for late payment. Total fine due: {self.fine_due}")
                # Optionally: update next_payment_date here if fine applies?
                # Or let the regular next payment date logic handle it after payment.

        # --- Process Payment --- 
        payment_made_this_save = self.paid_amount
        if payment_made_this_save > 0:
            # Decide how payment applies: Fine first, then principal? 
            # Simple approach: Just add to total_paid. Fine is tracked separately.
            self.total_paid += payment_made_this_save
            # If payment covers outstanding fine, reduce fine_due
            if payment_made_this_save >= self.fine_due:
                 payment_after_fine = payment_made_this_save - self.fine_due
                 self.fine_due = Decimal('0.00') 
                 # What to do with payment_after_fine? Assume it covers interval payment.
            else:
                self.fine_due -= payment_made_this_save # Reduce fine by amount paid

            # Reset paid_amount for next transaction
            self.paid_amount = Decimal("0.00")

            # --- Recalculate Next Payment Date after a payment is made --- 
            if self.policy_holder.payment_interval != "Single" and self.payment_status != 'Paid':
                 # Calculate based on the *previous* next_payment_date or start_date
                 last_due_date = self.next_payment_date or self.policy_holder.start_date
                 self.next_payment_date = self.calculate_next_payment_date(last_due_date)

        # --- Update Statuses and Calculated Fields --- 
        # Ensure total_premium and total_paid are Decimal
        self.total_premium = Decimal(str(self.total_premium)) if self.total_premium is not None else Decimal('0.00')
        self.total_paid = Decimal(str(self.total_paid)) if self.total_paid is not None else Decimal('0.00')
        
        self.remaining_premium = max(self.total_premium - self.total_paid, Decimal("0.00"))

        if self.total_paid >= self.total_premium and self.total_premium > 0:
            self.payment_status = "Paid"
            self.next_payment_date = None # No next date if fully paid
        elif self.total_paid > 0:
            self.payment_status = "Partially Paid"
        else:
            self.payment_status = "Unpaid"

        # --- GSV/SSV Calculations --- 
        # These methods should ideally handle potential missing data gracefully
        try:
            self.gsv_value = GSVRate.calculate_gsv(self)
        except Exception as e:
            print(f"Error calculating GSV: {e}")
            self.gsv_value = Decimal('0.00')
        try:
             self.ssv_value = SSVConfig.calculate_ssv(self)
        except Exception as e:
            print(f"Error calculating SSV: {e}")
            self.ssv_value = Decimal('0.00')

        # Call full_clean to run validations (including our custom clean method)
        self.full_clean()

        super().save(*args, **kwargs)

    def calculate_next_payment_date(self, base_date):
        """Helper to calculate next payment date based on interval and a base date."""
        if self.policy_holder.payment_interval == "Single":
            return None
           
        interval_months = {"quarterly": 3, "semi_annual": 6, "annual": 12}.get(
            self.policy_holder.payment_interval
        )
        if interval_months and base_date:
            # Calculate months to add
            total_months = base_date.month + interval_months
            year_increase = (total_months - 1) // 12
            new_month = (total_months - 1) % 12 + 1
            new_year = base_date.year + year_increase
            # Handle potential day issues (e.g., Feb 31)
            # Find the last day of the target month
            import calendar
            last_day = calendar.monthrange(new_year, new_month)[1]
            new_day = min(base_date.day, last_day)
            return date(new_year, new_month, new_day)
        return None # Return None if interval or base_date is invalid

    # --- New method for Estimated Maturity Value ---
    def calculate_estimated_maturity_value(self) -> Decimal:
        """Calculates an *estimated* maturity value based on policy details."""
        # Add check: If no policy_holder is associated yet, return 0
        if not self.policy_holder:
            return Decimal("0.00")
            
        try:
            ph = self.policy_holder # ph assignment happens here
            policy = ph.policy
            # ... (rest of the try block remains the same) ...
            sum_assured = ph.sum_assured or Decimal('0.00')
            annual_premium = self.annual_premium or Decimal('0.00')
            policy_term = Decimal(str(ph.duration_years)) if ph.duration_years else Decimal('0')

            guaranteed_rate = policy.guaranteed_interest_rate if policy.guaranteed_interest_rate is not None else Decimal('0.0000')
            terminal_rate = policy.terminal_bonus_rate if policy.terminal_bonus_rate is not None else Decimal('0.0000')
            annual_bonus_rate = Decimal('0.045') 

            if guaranteed_rate > 0 and annual_premium > 0 and policy_term > 0:
                future_value_factor = ((Decimal(1) + guaranteed_rate)**policy_term - Decimal(1)) / guaranteed_rate
                guaranteed_additions_future_value = annual_premium * future_value_factor
            else:
                guaranteed_additions_future_value = annual_premium * policy_term

            annual_bonus_component = sum_assured * annual_bonus_rate * policy_term
            terminal_bonus_component = sum_assured * terminal_rate

            maturity_value = (
                sum_assured + 
                guaranteed_additions_future_value + 
                annual_bonus_component + 
                terminal_bonus_component
            )
            
            return maturity_value.quantize(Decimal("1.00"))

        except Exception as e:
            # Safely access policy_holder id in except block
            policy_holder_id = getattr(self.policy_holder, 'id', 'N/A') 
            print(f"Error calculating estimated maturity value for PolicyHolder {policy_holder_id}: {e}")
            # Optionally log the error
            return Decimal("0.00")
    # --- End of new method ---

    class Meta:
        verbose_name = "Premium Payment"
        verbose_name_plural = "Premium Payments"

    def __str__(self):
        return f"Premium Payment for {self.policy_holder} ({self.payment_status})"

#Agent report Model

class AgentReport(models.Model):
    agent = models.ForeignKey(SalesAgent, on_delete=models.CASCADE)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="agent_reports", default=1
    )
    report_date = models.DateField()
    reporting_period = models.CharField(max_length=20)
    policies_sold = models.IntegerField(default=0)
    total_premium = models.DecimalField(max_digits=12, decimal_places=2)
    commission_earned = models.DecimalField(max_digits=10, decimal_places=2)
    target_achievement = models.DecimalField(max_digits=5, decimal_places=2)
    renewal_rate = models.DecimalField(max_digits=5, decimal_places=2)
    customer_retention = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Report for {self.agent} on {self.report_date}"

    class Meta:
        verbose_name = "Agent Report"
        verbose_name_plural = "Agent Reports"

#Loan Model 

class Loan(models.Model):
    policy_holder = models.ForeignKey(
        "PolicyHolder", on_delete=models.CASCADE, related_name="loans"
    )
    loan_amount = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Principal loan amount."
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Annual interest rate in percentage.",
    )
    remaining_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Remaining loan principal balance.",
    )
    accrued_interest = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Interest accrued on the loan.",
    )
    loan_status = models.CharField(
        max_length=50,
        choices=[("Active", "Active"), ("Paid", "Paid")],
        default="Active",
    )
    last_interest_date = models.DateField(
        auto_now_add=True, help_text="Date when interest was last accrued."
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    def calculate_max_loan(
        self, requested_amount: Decimal = None
    ) -> Dict[str, Union[bool, str, Decimal]]:
        """
        Calculate maximum loan amount and validate requested amount if provided.
        """
        try:
            premium_payment = self.policy_holder.premium_payments.first()
            if not premium_payment:
                return {
                    "is_valid": False,
                    "message": "No premium payments found for policy holder",
                    "max_allowed": Decimal("0"),
                    "gsv_value": Decimal("0"),
                }

            gsv = premium_payment.gsv_value
            max_loan = gsv * Decimal("0.90")

            result = {
                "is_valid": True,
                "message": "Maximum loan amount calculated",
                "max_allowed": max_loan,
                "gsv_value": gsv,
            }

            if requested_amount is not None:
                if requested_amount <= Decimal("0"):
                    result.update(
                        {
                            "is_valid": False,
                            "message": "Loan amount must be greater than 0",
                            "requested_amount": requested_amount,
                        }
                    )
                elif requested_amount > max_loan:
                    result.update(
                        {
                            "is_valid": False,
                            "message": f"Loan amount exceeds maximum allowed amount of {max_loan}",
                            "requested_amount": requested_amount,
                        }
                    )
                else:
                    result.update(
                        {
                            "message": "Loan amount is valid",
                            "requested_amount": requested_amount,
                        }
                    )

            return result

        except Exception as e:
            return {
                "is_valid": False,
                "message": f"Error calculating maximum loan: {str(e)}",
                "max_allowed": Decimal("0"),
                "gsv_value": Decimal("0"),
            }

    def clean(self):
        """Validate the loan before saving."""
        if not self.pk:  # Only validate on creation
            validation = self.calculate_max_loan(self.loan_amount)
            if not validation["is_valid"]:
                raise ValidationError({"loan_amount": validation["message"]})

    def save(self, *args, **kwargs):
        """Save the loan with validation."""
        try:
            self.full_clean()  # This will call our clean() method
            if not self.pk:  # On loan creation
                self.remaining_balance = self.loan_amount
            super().save(*args, **kwargs)
        except ValidationError as e:
            raise ValidationError(e.message_dict)
        except Exception as e:
            raise ValidationError(
                {"non_field_errors": [f"Error saving loan: {str(e)}"]}
            )

    def accrue_interest(self):
        """Accrue interest on the remaining balance."""
        if self.loan_status != "Active":
            return

        today = date.today()
        days_since_last_accrual = (today - self.last_interest_date).days

        if days_since_last_accrual <= 0:
            return

        try:
            daily_rate = self.interest_rate / 100 / 365
            interest = (
                self.remaining_balance
                * Decimal(daily_rate)
                * Decimal(days_since_last_accrual)
            )

            self.accrued_interest += interest.quantize(Decimal("1.00"))
            self.last_interest_date = today
            self.save()
        except Exception as e:
            raise ValidationError(f"Error accruing interest: {str(e)}")

    def __str__(self):
        return f"Loan for {self.policy_holder} - {self.loan_status}"


# Loan Repayment Model

class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="repayments")
    repayment_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Amount paid towards the loan."
    )
    repayment_type = models.CharField(
        max_length=50,
        choices=[
            ("Principal", "Principal"),
            ("Interest", "Interest"),
            ("Both", "Both"),
        ],
        default="Both",
    )
    remaining_loan_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Remaining loan balance after this repayment.",
    )

    def process_repayment(self):
        """Apply repayment to interest and/or principal."""
        remaining = self.amount

        if self.repayment_type in ("Both", "Interest"):
            # Deduct from accrued interest first
            interest_payment = min(remaining, self.loan.accrued_interest)
            self.loan.accrued_interest -= interest_payment
            remaining -= interest_payment

        if self.repayment_type in ("Both", "Principal") and remaining > 0:
            # Deduct from remaining balance
            principal_payment = min(remaining, self.loan.remaining_balance)
            self.loan.remaining_balance -= principal_payment

        # Update loan status
        if self.loan.remaining_balance <= 0 and self.loan.accrued_interest <= 0:
            self.loan.loan_status = "Paid"

        # Save the updated loan
        self.loan.save()

        # Set the remaining loan balance for this repayment
        self.remaining_loan_balance = (
            self.loan.remaining_balance + self.loan.accrued_interest
        )

    def save(self, *args, **kwargs):
        """Process repayment before saving."""
        self.process_repayment()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Repayment for {self.loan} on {self.repayment_date}"
