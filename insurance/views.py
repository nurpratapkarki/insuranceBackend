from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from insurance.models import (
    Occupation, MortalityRate, Company, Branch, InsurancePolicy, GSVRate, SSVConfig,
    AgentApplication, SalesAgent, DurationFactor, Customer, KYC, PolicyHolder,
    BonusRate, Bonus, ClaimRequest, ClaimProcessing, PaymentProcessing, Underwriting,
    PremiumPayment, AgentReport, Loan, LoanRepayment
)
from insurance.serializers import (
    OccupationSerializer, MortalityRateSerializer, CompanySerializer, BranchSerializer,
    GSVRateSerializer, SSVConfigSerializer, InsurancePolicySerializer, AgentApplicationSerializer,
    SalesAgentSerializer, DurationFactorSerializer, CustomerSerializer, KYCSerializer,
    PolicyHolderSerializer, BonusRateSerializer, BonusSerializer, ClaimRequestSerializer,
    ClaimProcessingSerializer, PaymentProcessingSerializer, UnderwritingSerializer,
    PremiumPaymentSerializer, AgentReportSerializer, LoanSerializer, LoanRepaymentSerializer
)

# Occupation views
@api_view(['GET', 'POST'])
def occupation_list(request):
    if request.method == 'GET':
        occupations = Occupation.objects.all()
        serializer = OccupationSerializer(occupations, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = OccupationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def occupation_detail(request, pk):
    occupation = get_object_or_404(Occupation, pk=pk)
    
    if request.method == 'GET':
        serializer = OccupationSerializer(occupation)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = OccupationSerializer(occupation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        occupation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Mortality Rate views
@api_view(['GET', 'POST'])
def mortality_rate_list(request):
    if request.method == 'GET':
        mortality_rates = MortalityRate.objects.all()
        serializer = MortalityRateSerializer(mortality_rates, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = MortalityRateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def mortality_rate_detail(request, pk):
    mortality_rate = get_object_or_404(MortalityRate, pk=pk)
    
    if request.method == 'GET':
        serializer = MortalityRateSerializer(mortality_rate)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = MortalityRateSerializer(mortality_rate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        mortality_rate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Company views
@api_view(['GET', 'POST'])
def company_list(request):
    if request.method == 'GET':
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'GET':
        serializer = CompanySerializer(company)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Branch views
@api_view(['GET', 'POST'])
def branch_list(request):
    if request.method == 'GET':
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def branch_detail(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    
    if request.method == 'GET':
        serializer = BranchSerializer(branch)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BranchSerializer(branch, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        branch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Insurance Policy views
@api_view(['GET', 'POST'])
def insurance_policy_list(request):
    if request.method == 'GET':
        policies = InsurancePolicy.objects.all()
        serializer = InsurancePolicySerializer(policies, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = InsurancePolicySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def insurance_policy_detail(request, pk):
    policy = get_object_or_404(InsurancePolicy, pk=pk)
    
    if request.method == 'GET':
        serializer = InsurancePolicySerializer(policy)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = InsurancePolicySerializer(policy, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        policy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# GSV Rate views
@api_view(['GET', 'POST'])
def gsv_rate_list(request):
    if request.method == 'GET':
        gsv_rates = GSVRate.objects.all()
        serializer = GSVRateSerializer(gsv_rates, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = GSVRateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def gsv_rate_detail(request, pk):
    gsv_rate = get_object_or_404(GSVRate, pk=pk)
    
    if request.method == 'GET':
        serializer = GSVRateSerializer(gsv_rate)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = GSVRateSerializer(gsv_rate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        gsv_rate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# SSV Config views
@api_view(['GET', 'POST'])
def ssv_config_list(request):
    if request.method == 'GET':
        ssv_configs = SSVConfig.objects.all()
        serializer = SSVConfigSerializer(ssv_configs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = SSVConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def ssv_config_detail(request, pk):
    ssv_config = get_object_or_404(SSVConfig, pk=pk)
    
    if request.method == 'GET':
        serializer = SSVConfigSerializer(ssv_config)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = SSVConfigSerializer(ssv_config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        ssv_config.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Agent Application views
@api_view(['GET', 'POST'])
def agent_application_list(request):
    if request.method == 'GET':
        applications = AgentApplication.objects.all()
        serializer = AgentApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = AgentApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def agent_application_detail(request, pk):
    application = get_object_or_404(AgentApplication, pk=pk)
    
    if request.method == 'GET':
        serializer = AgentApplicationSerializer(application)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AgentApplicationSerializer(application, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Sales Agent views
@api_view(['GET', 'POST'])
def sales_agent_list(request):
    if request.method == 'GET':
        agents = SalesAgent.objects.all()
        serializer = SalesAgentSerializer(agents, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = SalesAgentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def sales_agent_detail(request, pk):
    agent = get_object_or_404(SalesAgent, pk=pk)
    
    if request.method == 'GET':
        serializer = SalesAgentSerializer(agent)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = SalesAgentSerializer(agent, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        agent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Duration Factor views
@api_view(['GET', 'POST'])
def duration_factor_list(request):
    if request.method == 'GET':
        factors = DurationFactor.objects.all()
        serializer = DurationFactorSerializer(factors, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = DurationFactorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def duration_factor_detail(request, pk):
    factor = get_object_or_404(DurationFactor, pk=pk)
    
    if request.method == 'GET':
        serializer = DurationFactorSerializer(factor)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = DurationFactorSerializer(factor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        factor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Customer views
@api_view(['GET', 'POST'])
def customer_list(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'GET':
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# KYC views
@api_view(['GET', 'POST'])
def kyc_list(request):
    if request.method == 'GET':
        kycs = KYC.objects.all()
        serializer = KYCSerializer(kycs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = KYCSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def kyc_detail(request, pk):
    kyc = get_object_or_404(KYC, pk=pk)
    
    if request.method == 'GET':
        serializer = KYCSerializer(kyc)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = KYCSerializer(kyc, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        kyc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Policy Holder views
@api_view(['GET', 'POST'])
def policy_holder_list(request):
    if request.method == 'GET':
        holders = PolicyHolder.objects.all()
        serializer = PolicyHolderSerializer(holders, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PolicyHolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def policy_holder_detail(request, pk):
    holder = get_object_or_404(PolicyHolder, pk=pk)
    
    if request.method == 'GET':
        serializer = PolicyHolderSerializer(holder)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PolicyHolderSerializer(holder, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        holder.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Bonus Rate views
@api_view(['GET', 'POST'])
def bonus_rate_list(request):
    if request.method == 'GET':
        rates = BonusRate.objects.all()
        serializer = BonusRateSerializer(rates, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BonusRateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def bonus_rate_detail(request, pk):
    rate = get_object_or_404(BonusRate, pk=pk)
    
    if request.method == 'GET':
        serializer = BonusRateSerializer(rate)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BonusRateSerializer(rate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        rate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Bonus views
@api_view(['GET', 'POST'])
def bonus_list(request):
    if request.method == 'GET':
        bonuses = Bonus.objects.all()
        serializer = BonusSerializer(bonuses, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BonusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def bonus_detail(request, pk):
    bonus = get_object_or_404(Bonus, pk=pk)
    
    if request.method == 'GET':
        serializer = BonusSerializer(bonus)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BonusSerializer(bonus, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        bonus.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Claim Request views
@api_view(['GET', 'POST'])
def claim_request_list(request):
    if request.method == 'GET':
        claims = ClaimRequest.objects.all()
        serializer = ClaimRequestSerializer(claims, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ClaimRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def claim_request_detail(request, pk):
    claim = get_object_or_404(ClaimRequest, pk=pk)
    
    if request.method == 'GET':
        serializer = ClaimRequestSerializer(claim)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ClaimRequestSerializer(claim, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        claim.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Claim Processing views
@api_view(['GET', 'POST'])
def claim_processing_list(request):
    if request.method == 'GET':
        processing = ClaimProcessing.objects.all()
        serializer = ClaimProcessingSerializer(processing, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ClaimProcessingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def claim_processing_detail(request, pk):
    processing = get_object_or_404(ClaimProcessing, pk=pk)
    
    if request.method == 'GET':
        serializer = ClaimProcessingSerializer(processing)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ClaimProcessingSerializer(processing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        processing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Payment Processing views
@api_view(['GET', 'POST'])
def payment_processing_list(request):
    if request.method == 'GET':
        payments = PaymentProcessing.objects.all()
        serializer = PaymentProcessingSerializer(payments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PaymentProcessingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def payment_processing_detail(request, pk):
    payment = get_object_or_404(PaymentProcessing, pk=pk)
    
    if request.method == 'GET':
        serializer = PaymentProcessingSerializer(payment)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PaymentProcessingSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Underwriting views
@api_view(['GET', 'POST'])
def underwriting_list(request):
    if request.method == 'GET':
        underwritings = Underwriting.objects.all()
        serializer = UnderwritingSerializer(underwritings, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = UnderwritingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def underwriting_detail(request, pk):
    underwriting = get_object_or_404(Underwriting, pk=pk)
    
    if request.method == 'GET':
        serializer = UnderwritingSerializer(underwriting)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UnderwritingSerializer(underwriting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        underwriting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Premium Payment views
@api_view(['GET', 'POST'])
def premium_payment_list(request):
    if request.method == 'GET':
        payments = PremiumPayment.objects.all()
        serializer = PremiumPaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PremiumPaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def premium_payment_detail(request, pk):
    payment = get_object_or_404(PremiumPayment, pk=pk)
    
    if request.method == 'GET':
        serializer = PremiumPaymentSerializer(payment)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PremiumPaymentSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Agent Report views
@api_view(['GET', 'POST'])
def agent_report_list(request):
    if request.method == 'GET':
        reports = AgentReport.objects.all()
        serializer = AgentReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = AgentReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def agent_report_detail(request, pk):
    report = get_object_or_404(AgentReport, pk=pk)
    
    if request.method == 'GET':
        serializer = AgentReportSerializer(report)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AgentReportSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Loan views
@api_view(['GET', 'POST'])
def loan_list(request):
    if request.method == 'GET':
        loans = Loan.objects.all()
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def loan_detail(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    
    if request.method == 'GET':
        serializer = LoanSerializer(loan)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = LoanSerializer(loan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        loan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Loan Repayment views
@api_view(['GET', 'POST'])
def loan_repayment_list(request):
    if request.method == 'GET':
        repayments = LoanRepayment.objects.all()
        serializer = LoanRepaymentSerializer(repayments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = LoanRepaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def loan_repayment_detail(request, pk):
    repayment = get_object_or_404(LoanRepayment, pk=pk)
    
    if request.method == 'GET':
        serializer = LoanRepaymentSerializer(repayment)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = LoanRepaymentSerializer(repayment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        repayment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)