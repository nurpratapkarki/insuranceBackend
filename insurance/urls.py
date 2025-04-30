from django.urls import path, include
from rest_framework.routers import DefaultRouter
from insurance import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'occupations', views.OccupationViewSet)
router.register(r'mortality-rates', views.MortalityRateViewSet)
router.register(r'companies', views.CompanyViewSet)
router.register(r'branches', views.BranchViewSet)
router.register(r'insurance-policies', views.InsurancePolicyViewSet)
router.register(r'gsv-rates', views.GSVRateViewSet)
router.register(r'ssv-configs', views.SSVConfigViewSet)
router.register(r'agent-applications', views.AgentApplicationViewSet)
router.register(r'sales-agents', views.SalesAgentViewSet)
router.register(r'duration-factors', views.DurationFactorViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'kyc', views.KYCViewSet)
router.register(r'policy-holders', views.PolicyHolderViewSet)
router.register(r'bonus-rates', views.BonusRateViewSet)
router.register(r'bonuses', views.BonusViewSet)
router.register(r'claim-requests', views.ClaimRequestViewSet)
router.register(r'claim-processing', views.ClaimProcessingViewSet)
router.register(r'payment-processing', views.PaymentProcessingViewSet)
router.register(r'underwriting', views.UnderwritingViewSet)
router.register(r'premium-payments', views.PremiumPaymentViewSet)
router.register(r'agent-reports', views.AgentReportViewSet)
router.register(r'loans', views.LoanViewSet)
router.register(r'loan-repayments', views.LoanRepaymentViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)), # Include the router-generated URLs
    path('home/', views.HomeDataView.as_view(), name='api-home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]