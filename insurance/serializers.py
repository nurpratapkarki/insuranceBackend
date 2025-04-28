from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from insurance.models import (
    Occupation, MortalityRate, Company, Branch, InsurancePolicy, GSVRate, SSVConfig,
    AgentApplication, SalesAgent, DurationFactor, Customer, KYC, PolicyHolder,
    BonusRate, Bonus, ClaimRequest, ClaimProcessing, PaymentProcessing, Underwriting,
    PremiumPayment, AgentReport, Loan, LoanRepayment
)

class OccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = '__all__'

class MortalityRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MortalityRate
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    
    class Meta:
        model = Branch
        fields = '__all__'

class GSVRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GSVRate
        fields = '__all__'

class SSVConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSVConfig
        fields = '__all__'

class InsurancePolicySerializer(serializers.ModelSerializer):
    gsv_rates = GSVRateSerializer(many=True, read_only=True)
    ssv_configs = SSVConfigSerializer(many=True, read_only=True)
    
    class Meta:
        model = InsurancePolicy
        fields = '__all__'

class AgentApplicationSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name')
    
    class Meta:
        model = AgentApplication
        fields = '__all__'

class SalesAgentSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name')
    agent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesAgent
        fields = '__all__'
    
    def get_agent_name(self, obj):
        if obj.application:
            return f"{obj.application.first_name} {obj.application.last_name}"
        return obj.agent_code

class DurationFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DurationFactor
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Customer
        fields = '__all__'
        depth = 10
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data.get('password'))
        return super().update(instance, validated_data)

class KYCSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.get_full_name')
    
    class Meta:
        model = KYC
        fields = '__all__'

class PolicyHolderSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    policy_name = serializers.ReadOnlyField(source='policy.name')
    agent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PolicyHolder
        fields = '__all__'
        read_only_fields = ('age', 'maturity_date')
        depth = 1
    
    def get_customer_name(self, obj):
        if obj.customer:
            return f"{obj.customer.first_name} {obj.customer.last_name}"
        return "No Customer"
    
    def get_agent_name(self, obj):
        if obj.agent and obj.agent.application:
            return f"{obj.agent.application.first_name} {obj.agent.application.last_name}"
        return "No Agent"

class BonusRateSerializer(serializers.ModelSerializer):
    policy_name = serializers.ReadOnlyField(source='policy.name')
    
    class Meta:
        model = BonusRate
        fields = '__all__'

class BonusSerializer(serializers.ModelSerializer):
    policy_holder_number = serializers.ReadOnlyField(source='policy_holder.policy_number')
    
    class Meta:
        model = Bonus
        fields = '__all__'
        read_only_fields = ('accrued_amount',)

class ClaimRequestSerializer(serializers.ModelSerializer):
    policy_holder_number = serializers.ReadOnlyField(source='policy_holder.policy_number')
    customer_name = serializers.SerializerMethodField()
    branch_name = serializers.ReadOnlyField(source='branch.name')
    
    class Meta:
        model = ClaimRequest
        fields = '__all__'
        read_only_fields = ('claim_amount',)
    
    def get_customer_name(self, obj):
        if obj.policy_holder and obj.policy_holder.customer:
            return f"{obj.policy_holder.customer.first_name} {obj.policy_holder.customer.last_name}"
        return "No Customer"

class ClaimProcessingSerializer(serializers.ModelSerializer):
    claim_number = serializers.SerializerMethodField()
    branch_name = serializers.ReadOnlyField(source='branch.name')
    company_name = serializers.ReadOnlyField(source='company.name')
    
    class Meta:
        model = ClaimProcessing
        fields = '__all__'
    
    def get_claim_number(self, obj):
        return f"Claim #{obj.claim_request.id}"

class PaymentProcessingSerializer(serializers.ModelSerializer):
    claim_number = serializers.SerializerMethodField()
    branch_name = serializers.ReadOnlyField(source='branch.name')
    company_name = serializers.ReadOnlyField(source='company.name')
    
    class Meta:
        model = PaymentProcessing
        fields = '__all__'
        read_only_fields = ('amount_paid', 'payment_date')
    
    def get_claim_number(self, obj):
        return f"Claim #{obj.claim_request.id}"

class UnderwritingSerializer(serializers.ModelSerializer):
    policy_holder_number = serializers.ReadOnlyField(source='policy_holder.policy_number')
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Underwriting
        fields = '__all__'
        read_only_fields = ('last_updated_at',)
    
    def get_customer_name(self, obj):
        if obj.policy_holder and obj.policy_holder.customer:
            return f"{obj.policy_holder.customer.first_name} {obj.policy_holder.customer.last_name}"
        return "No Customer"

class PremiumPaymentSerializer(serializers.ModelSerializer):
    policy_holder_number = serializers.ReadOnlyField(source='policy_holder.policy_number')
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PremiumPayment
        fields = '__all__'
        read_only_fields = ('annual_premium', 'interval_payment', 'total_paid', 
                           'total_premium', 'remaining_premium', 'gsv_value', 'ssv_value')
    
    def get_customer_name(self, obj):
        if obj.policy_holder and obj.policy_holder.customer:
            return f"{obj.policy_holder.customer.first_name} {obj.policy_holder.customer.last_name}"
        return "No Customer"

class AgentReportSerializer(serializers.ModelSerializer):
    agent_name = serializers.SerializerMethodField()
    branch_name = serializers.ReadOnlyField(source='branch.name')
    
    class Meta:
        model = AgentReport
        fields = '__all__'
    
    def get_agent_name(self, obj):
        if obj.agent and obj.agent.application:
            return f"{obj.agent.application.first_name} {obj.agent.application.last_name}"
        return obj.agent.agent_code

class LoanSerializer(serializers.ModelSerializer):
    policy_holder_number = serializers.ReadOnlyField(source='policy_holder.policy_number')
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = '__all__'
        read_only_fields = ('remaining_balance', 'accrued_interest', 
                           'last_interest_date', 'created_at', 'updated_at')
    
    def get_customer_name(self, obj):
        if obj.policy_holder and obj.policy_holder.customer:
            return f"{obj.policy_holder.customer.first_name} {obj.policy_holder.customer.last_name}"
        return "No Customer"
    
    def validate_loan_amount(self, value):
        """
        Validate the loan amount against the policy's maximum allowed value.
        """
        policy_holder = self.context.get('policy_holder')
        if policy_holder:
            loan = Loan(policy_holder=policy_holder, loan_amount=value)
            validation = loan.calculate_max_loan(value)
            if not validation['is_valid']:
                raise serializers.ValidationError(validation['message'])
        return value

class LoanRepaymentSerializer(serializers.ModelSerializer):
    loan_id = serializers.ReadOnlyField(source='loan.id')
    policy_holder_number = serializers.SerializerMethodField()
    
    class Meta:
        model = LoanRepayment
        fields = '__all__'
        read_only_fields = ('remaining_loan_balance',)
    
    def get_policy_holder_number(self, obj):
        if obj.loan and obj.loan.policy_holder:
            return obj.loan.policy_holder.policy_number
        return "No Policy"