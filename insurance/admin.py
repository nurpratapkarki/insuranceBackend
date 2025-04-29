from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from insurance.models import (
    Occupation, MortalityRate, Company, Branch, InsurancePolicy, GSVRate, SSVConfig,
    AgentApplication, SalesAgent, DurationFactor, Customer, KYC, PolicyHolder,
    BonusRate, Bonus, ClaimRequest, ClaimProcessing, PaymentProcessing, Underwriting,
    PremiumPayment, AgentReport, Loan, LoanRepayment, User
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'user_type')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'gender')}),
        (('User type'), {'fields': ('user_type', 'branch', 'agent')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'user_type'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ('name', 'risk_category')
    search_fields = ('name',)
    list_filter = ('risk_category',)


@admin.register(MortalityRate)
class MortalityRateAdmin(admin.ModelAdmin):
    list_display = ('age_group_start', 'age_group_end', 'rate')
    list_filter = ('age_group_start', 'age_group_end')
    ordering = ('age_group_start',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_code', 'email', 'phone_number', 'is_active')
    search_fields = ('name', 'company_code', 'email')
    list_filter = ('is_active',)
    readonly_fields = ('id',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" height="100" />', obj.logo.url)
        return "No Logo"
    
    logo_preview.short_description = 'Logo Preview'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'company_code', 'email', 'phone_number', 'is_active')
        }),
        ('Address', {
            'fields': ('address',)
        }),
        ('Media', {
            'fields': ('logo', 'logo_preview')
        }),
    )
    readonly_fields = ('logo_preview',)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch_code', 'location', 'company', 'get_user_username')
    search_fields = ('name', 'branch_code', 'location', 'user__username')
    list_filter = ('company',)
    raw_id_fields = ('user',)
    autocomplete_fields = ['user']

    def get_user_username(self, obj):
        if obj.user:
            return obj.user.username
        return None
    get_user_username.short_description = 'Branch Admin User'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'user' in form.base_fields:
            form.base_fields['user'].queryset = User.objects.filter(user_type='branch')
        return form

class GSVRateInline(admin.StackedInline):
    model = GSVRate
    extra = 0
    fields = ('min_year', 'max_year', 'rate')
    verbose_name_plural = 'GSV Rates'

class SSVConfigInline(admin.StackedInline):
    model = SSVConfig
    extra = 0
    fields = ('min_year', 'max_year', 'ssv_factor', 'eligibility_years')
    verbose_name_plural = 'SSV Configurations'



@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'policy_code', 'policy_type', 'base_multiplier', 'min_sum_assured', 'max_sum_assured')
    search_fields = ('name', 'policy_code')
    list_filter = ('policy_type', 'include_adb', 'include_ptd')
    readonly_fields = ('created_at',)
    inlines = [GSVRateInline, SSVConfigInline]




@admin.register(AgentApplication)
class AgentApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'branch', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('branch', 'status', 'gender', 'created_at')
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'gender', 'date_of_birth', 'branch')
        }),
        ('Family Information', {
            'fields': ('father_name', 'mother_name', 'grand_father_name', 'grand_mother_name')
        }),
        ('Address', {
            'fields': ('address',)
        }),
        ('Documents', {
            'fields': ('resume', 'citizenship_front', 'citizenship_back', 'license_front', 'license_back', 'pp_photo')
        }),
        ('License Information', {
            'fields': ('license_number', 'license_issue_date', 'license_expiry_date', 'license_type', 
                      'license_issue_district', 'license_issue_zone', 'license_issue_province', 'license_issue_country')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )


@admin.register(SalesAgent)
class SalesAgentAdmin(admin.ModelAdmin):
    list_display = ('get_agent_name', 'agent_code', 'branch', 'joining_date', 'is_active', 'status')
    search_fields = ('agent_code', 'application__first_name', 'application__last_name', 'application__email')
    list_filter = ('branch', 'is_active', 'status', 'joining_date')
    readonly_fields = ('id', 'total_policies_sold', 'total_premium_collected', 'last_policy_date')
    
    def get_agent_name(self, obj):
        if obj.application:
            return f"{obj.application.first_name} {obj.application.last_name}"
        return obj.agent_code
    get_agent_name.short_description = 'Agent Name'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('application', 'agent_code', 'branch', 'is_active', 'status')
        }),
        ('Commission Details', {
            'fields': ('commission_rate',)
        }),
        ('Employment Dates', {
            'fields': ('joining_date', 'termination_date', 'termination_reason')
        }),
        ('Performance Metrics', {
            'fields': ('total_policies_sold', 'total_premium_collected', 'last_policy_date')
        }),
    )


class BonusInline(admin.TabularInline):
    model = Bonus
    extra = 0
    fields = ('bonus_type', 'accrued_amount', 'start_date')
    readonly_fields = ('accrued_amount',)
    verbose_name_plural = 'Bonuses'

@admin.register(DurationFactor)
class DurationFactorAdmin(admin.ModelAdmin):
    list_display = ('min_duration', 'max_duration', 'factor', 'policy_type')
    search_fields = ('policy_type',)
    list_filter = ('policy_type',)

class KYCInline(admin.StackedInline):
    model = KYC
    extra = 0
    can_delete = False
    verbose_name_plural = 'KYC Information'

# --- Inline for PolicyHolders ---
class PolicyHolderInline(admin.StackedInline):
    model = PolicyHolder
    extra = 0
    readonly_fields = ('policy_number', 'start_date', 'maturity_date')
    can_delete = False
    verbose_name_plural = 'policies'

# --- Main Customer Admin ---

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_name', 'email', 'phone_number', 'get_user_username', 'created_at')
    list_filter = ('created_at', 'gender')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [KYCInline, PolicyHolderInline,BonusInline]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Full Name'
    
    def get_user_username(self, obj):
        if obj.user:
            return obj.user.username
        return None
    get_user_username.short_description = 'Username'

@admin.register(BonusRate)
class BonusRateAdmin(admin.ModelAdmin):
    list_display = ('policy', 'year', 'min_year', 'max_year', 'bonus_per_thousand')
    search_fields = ('policy__name',)
    list_filter = ('policy', 'year')


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('policy_holder', 'branch', 'claim_date', 'status', 'reason', 'claim_amount')
    search_fields = ('policy_holder__policy_number', 'policy_holder__customer__first_name')
    list_filter = ('branch', 'status', 'claim_date')
    readonly_fields = ('claim_amount',)


@admin.register(ClaimProcessing)
class ClaimProcessingAdmin(admin.ModelAdmin):
    list_display = ('claim_request', 'branch', 'company', 'processing_status', 'processed_at')
    search_fields = ('claim_request__policy_holder__policy_number',)
    list_filter = ('branch', 'company', 'processing_status', 'processed_at')
    readonly_fields = ('processed_at',)

    actions = ['approve_claim', 'reject_claim']
    
    def approve_claim(self, request, queryset):
        for claim_processing in queryset:
            claim_processing.processing_status = 'Approved'
            claim_processing.save()
            claim_processing.finalize_claim()
        self.message_user(request, f"{queryset.count()} claim(s) have been approved.")
    approve_claim.short_description = "Approve selected claims"
    
    def reject_claim(self, request, queryset):
        for claim_processing in queryset:
            claim_processing.processing_status = 'Rejected'
            claim_processing.save()
            claim_processing.finalize_claim()
        self.message_user(request, f"{queryset.count()} claim(s) have been rejected.")
    reject_claim.short_description = "Reject selected claims"


@admin.register(PaymentProcessing)
class PaymentProcessingAdmin(admin.ModelAdmin):
    list_display = ('claim_request', 'branch', 'company', 'processing_status', 'amount_paid', 'payment_date')
    search_fields = ('claim_request__policy_holder__policy_number',)
    list_filter = ('branch', 'company', 'processing_status', 'payment_date')
    readonly_fields = ('amount_paid', 'payment_date')


@admin.register(Underwriting)
class UnderwritingAdmin(admin.ModelAdmin):
    list_display = ('policy_holder', 'risk_assessment_score', 'risk_category', 'manual_override', 'last_updated_by')
    search_fields = ('policy_holder__policy_number', 'policy_holder__customer__first_name')
    list_filter = ('risk_category', 'manual_override', 'last_updated_by')
    readonly_fields = ('last_updated_at',)


@admin.register(PremiumPayment)
class PremiumPaymentAdmin(admin.ModelAdmin):
    list_display = ('policy_holder', 'annual_premium', 'total_paid', 'next_payment_date', 'payment_status')
    search_fields = ('policy_holder__policy_number', 'policy_holder__customer__first_name')
    list_filter = ('payment_status',)
    readonly_fields = ('annual_premium', 'interval_payment', 'total_paid', 'total_premium', 
                       'remaining_premium', 'gsv_value', 'ssv_value')


@admin.register(AgentReport)
class AgentReportAdmin(admin.ModelAdmin):
    list_display = ('agent', 'branch', 'report_date', 'policies_sold', 'total_premium', 'commission_earned')
    search_fields = ('agent__agent_code', 'agent__application__first_name')
    list_filter = ('branch', 'report_date')


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('policy_holder', 'loan_amount', 'interest_rate', 'remaining_balance', 'loan_status', 'created_at')
    search_fields = ('policy_holder__policy_number', 'policy_holder__customer__first_name')
    list_filter = ('loan_status', 'created_at')
    readonly_fields = ('remaining_balance', 'accrued_interest', 'last_interest_date', 'created_at', 'updated_at')


@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'repayment_date', 'amount', 'repayment_type', 'remaining_loan_balance')
    search_fields = ('loan__policy_holder__policy_number',)
    list_filter = ('repayment_type', 'repayment_date')
    readonly_fields = ('remaining_loan_balance',)