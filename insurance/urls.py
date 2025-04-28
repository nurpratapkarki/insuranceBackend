from django.urls import path
from insurance import views

urlpatterns = [
    # Occupation URLs
    path('occupations/', views.occupation_list, name='occupation-list'),
    path('occupations/<int:pk>/', views.occupation_detail, name='occupation-detail'),
    
    # Mortality Rate URLs
    path('mortality-rates/', views.mortality_rate_list, name='mortality-rate-list'),
    path('mortality-rates/<int:pk>/', views.mortality_rate_detail, name='mortality-rate-detail'),
    
    # Company URLs
    path('companies/', views.company_list, name='company-list'),
    path('companies/<int:pk>/', views.company_detail, name='company-detail'),
    
    # Branch URLs
    path('branches/', views.branch_list, name='branch-list'),
    path('branches/<int:pk>/', views.branch_detail, name='branch-detail'),
    
    # Insurance Policy URLs
    path('insurance-policies/', views.insurance_policy_list, name='insurance-policy-list'),
    path('insurance-policies/<int:pk>/', views.insurance_policy_detail, name='insurance-policy-detail'),
    
    # GSV Rate URLs
    path('gsv-rates/', views.gsv_rate_list, name='gsv-rate-list'),
    path('gsv-rates/<int:pk>/', views.gsv_rate_detail, name='gsv-rate-detail'),
    
    # SSV Config URLs
    path('ssv-configs/', views.ssv_config_list, name='ssv-config-list'),
    path('ssv-configs/<int:pk>/', views.ssv_config_detail, name='ssv-config-detail'),
    
    # Agent Application URLs
    path('agent-applications/', views.agent_application_list, name='agent-application-list'),
    path('agent-applications/<int:pk>/', views.agent_application_detail, name='agent-application-detail'),
    
    # Sales Agent URLs
    path('sales-agents/', views.sales_agent_list, name='sales-agent-list'),
    path('sales-agents/<int:pk>/', views.sales_agent_detail, name='sales-agent-detail'),
    
    # Duration Factor URLs
    path('duration-factors/', views.duration_factor_list, name='duration-factor-list'),
    path('duration-factors/<int:pk>/', views.duration_factor_detail, name='duration-factor-detail'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customer-list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer-detail'),
    
    # KYC URLs
    path('kyc/', views.kyc_list, name='kyc-list'),
    path('kyc/<int:pk>/', views.kyc_detail, name='kyc-detail'),
    
    # Policy Holder URLs
    path('policy-holders/', views.policy_holder_list, name='policy-holder-list'),
    path('policy-holders/<int:pk>/', views.policy_holder_detail, name='policy-holder-detail'),
    
    # Bonus Rate URLs
    path('bonus-rates/', views.bonus_rate_list, name='bonus-rate-list'),
    path('bonus-rates/<int:pk>/', views.bonus_rate_detail, name='bonus-rate-detail'),
    
    # Bonus URLs
    path('bonuses/', views.bonus_list, name='bonus-list'),
    path('bonuses/<int:pk>/', views.bonus_detail, name='bonus-detail'),
    
    # Claim Request URLs
    path('claim-requests/', views.claim_request_list, name='claim-request-list'),
    path('claim-requests/<int:pk>/', views.claim_request_detail, name='claim-request-detail'),
    
    # Claim Processing URLs
    path('claim-processing/', views.claim_processing_list, name='claim-processing-list'),
    path('claim-processing/<int:pk>/', views.claim_processing_detail, name='claim-processing-detail'),
    
    # Payment Processing URLs
    path('payment-processing/', views.payment_processing_list, name='payment-processing-list'),
    path('payment-processing/<int:pk>/', views.payment_processing_detail, name='payment-processing-detail'),
    
    # Underwriting URLs
    path('underwriting/', views.underwriting_list, name='underwriting-list'),
    path('underwriting/<int:pk>/', views.underwriting_detail, name='underwriting-detail'),
    
    # Premium Payment URLs
    path('premium-payments/', views.premium_payment_list, name='premium-payment-list'),
    path('premium-payments/<int:pk>/', views.premium_payment_detail, name='premium-payment-detail'),
    
    # Agent Report URLs
    path('agent-reports/', views.agent_report_list, name='agent-report-list'),
    path('agent-reports/<int:pk>/', views.agent_report_detail, name='agent-report-detail'),
    
    # Loan URLs
    path('loans/', views.loan_list, name='loan-list'),
    path('loans/<int:pk>/', views.loan_detail, name='loan-detail'),
    
    # Loan Repayment URLs
    path('loan-repayments/', views.loan_repayment_list, name='loan-repayment-list'),
    path('loan-repayments/<int:pk>/', views.loan_repayment_detail, name='loan-repayment-detail'),
]