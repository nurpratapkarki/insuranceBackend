from rest_framework import status, viewsets, permissions as drf_permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from insurance.models import (
    Occupation, MortalityRate, Company, Branch, InsurancePolicy, GSVRate, SSVConfig,
    AgentApplication, SalesAgent, DurationFactor, Customer, KYC, PolicyHolder,
    BonusRate, Bonus, ClaimRequest, ClaimProcessing, PaymentProcessing, Underwriting,
    PremiumPayment, AgentReport, Loan, LoanRepayment, User
)
from insurance.serializers import (
    OccupationSerializer, MortalityRateSerializer, CompanySerializer, BranchSerializer,
    GSVRateSerializer, SSVConfigSerializer, InsurancePolicySerializer, AgentApplicationSerializer,
    SalesAgentSerializer, DurationFactorSerializer, CustomerSerializer, KYCSerializer,
    PolicyHolderSerializer, BonusRateSerializer, BonusSerializer, ClaimRequestSerializer,
    ClaimProcessingSerializer, PaymentProcessingSerializer, UnderwritingSerializer,
    PremiumPaymentSerializer, AgentReportSerializer, LoanSerializer, LoanRepaymentSerializer, UserSerializer
)

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_permissions(self):
        # More specific permissions can be set in subclasses or using action decorators
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Write operations typically require admin or specific roles
            return [IsAuthenticated()] 
        return [drf_permissions.IsAuthenticatedOrReadOnly()]



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        if user.is_superuser or user.is_staff:
            return User.objects.all()
       
        return User.objects.filter(pk=user.pk)



class OccupationViewSet(viewsets.ModelViewSet):
    queryset = Occupation.objects.all()
    serializer_class = OccupationSerializer
    permission_classes = [IsAuthenticated] 

class MortalityRateViewSet(viewsets.ModelViewSet):
    queryset = MortalityRate.objects.all()
    serializer_class = MortalityRateSerializer
    permission_classes = [IsAuthenticated] 
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated] 

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated] 

class InsurancePolicyViewSet(viewsets.ModelViewSet):
    queryset = InsurancePolicy.objects.all()
    serializer_class = InsurancePolicySerializer
    permission_classes = [IsAuthenticated] 

class GSVRateViewSet(viewsets.ModelViewSet):
    queryset = GSVRate.objects.all()
    serializer_class = GSVRateSerializer
    permission_classes = [IsAuthenticated]

class SSVConfigViewSet(viewsets.ModelViewSet):
    queryset = SSVConfig.objects.all()
    serializer_class = SSVConfigSerializer
    permission_classes = [IsAuthenticated]

class DurationFactorViewSet(viewsets.ModelViewSet):
    queryset = DurationFactor.objects.all()
    serializer_class = DurationFactorSerializer
    permission_classes = [IsAuthenticated]

class BonusRateViewSet(viewsets.ModelViewSet):
    queryset = BonusRate.objects.all()
    serializer_class = BonusRateSerializer
    permission_classes = [IsAuthenticated]

# --- Agent Related Models ---

class AgentApplicationViewSet(viewsets.ModelViewSet):
    queryset = AgentApplication.objects.all()
    serializer_class = AgentApplicationSerializer
    permission_classes = [IsAuthenticated] 
    
class SalesAgentViewSet(viewsets.ModelViewSet):
    queryset = SalesAgent.objects.all()
    serializer_class = SalesAgentSerializer
    permission_classes = [IsAuthenticated] 
    

# --- Customer and Policy Related Models ---

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_password(self, request, pk=None):
        customer = self.get_object()
        if customer.user:
            password = request.data.get('password')
            if password:
                customer.user.set_password(password)
                customer.user.save()
                return Response({'status': 'password set'})
            return Response({'error': 'No password provided'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'No user associated with this customer'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Note: User activation/deactivation might be better handled via the UserViewSet if needed


class KYCViewSet(viewsets.ModelViewSet):
    queryset = KYC.objects.all()
    serializer_class = KYCSerializer
    permission_classes = [IsAuthenticated] 
    
class PolicyHolderViewSet(viewsets.ModelViewSet):
    queryset = PolicyHolder.objects.all()
    serializer_class = PolicyHolderSerializer
    permission_classes = [IsAuthenticated]

class BonusViewSet(viewsets.ModelViewSet):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer
    permission_classes = [IsAuthenticated]


class ClaimRequestViewSet(viewsets.ModelViewSet):
    queryset = ClaimRequest.objects.all()
    serializer_class = ClaimRequestSerializer
    permission_classes = [IsAuthenticated] # Owner/Admin/Agent can create/view claims
    def perform_create(self, serializer):
         # Automatically set branch based on policy holder if possible, or require it
        policy_holder = serializer.validated_data.get('policy_holder')
        if policy_holder and policy_holder.branch:
             serializer.save(branch=policy_holder.branch)
        elif self.request.user.user_type == 'branch' and self.request.user.branch:
             serializer.save(branch=self.request.user.branch) # Branch admin creating claim?
        else:
             # Handle case where branch cannot be determined or raise validation error
             # For now, let serializer validation handle missing branch if required
             serializer.save()


class ClaimProcessingViewSet(viewsets.ModelViewSet):
    queryset = ClaimProcessing.objects.all()
    serializer_class = ClaimProcessingSerializer
    permission_classes = [IsAuthenticated] # Only Admin/Branch Admin process claims

    def perform_create(self, serializer):
        # Link company and branch automatically if possible
        claim_request = serializer.validated_data.get('claim_request')
        if claim_request:
            branch = claim_request.branch
            company = claim_request.branch.company if branch else None
            serializer.save(branch=branch, company=company)
        else:
            # Potentially raise error or handle based on request user's branch/company
             serializer.save()

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        processing = self.get_object()
        try:
            processing.finalize_claim()
            return Response({'status': f'Claim finalized with status {processing.processing_status}'})
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentProcessingViewSet(viewsets.ModelViewSet):
    queryset = PaymentProcessing.objects.all()
    serializer_class = PaymentProcessingSerializer
    permission_classes = [IsAuthenticated] 
        
    def perform_create(self, serializer):
        # Link company and branch automatically
        claim_request = serializer.validated_data.get('claim_request')
        if claim_request:
            branch = claim_request.branch
            company = claim_request.branch.company if branch else None
            serializer.save(branch=branch, company=company)
        else:
             serializer.save()


class UnderwritingViewSet(viewsets.ModelViewSet):
    queryset = Underwriting.objects.all()
    serializer_class = UnderwritingSerializer
    permission_classes = [IsAuthenticated] # Admin/Branch Admin manage underwriting
class PremiumPaymentViewSet(viewsets.ModelViewSet):
    queryset = PremiumPayment.objects.all()
    serializer_class = PremiumPaymentSerializer
    permission_classes = [IsAuthenticated] # Customer can view, Admin/Agent can manage

class AgentReportViewSet(viewsets.ModelViewSet):
    queryset = AgentReport.objects.all()
    serializer_class = AgentReportSerializer
    permission_classes = [IsAuthenticated] # Only Admin/Branch Admin manage agent reports

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated] # Customer/Admin/Agent access loans

   

    def get_serializer_context(self):
        # Pass policy_holder to serializer context for validation if creating/updating
        context = super().get_serializer_context()
        if self.action in ['create', 'update', 'partial_update'] and 'request' in context:
            policy_holder_id = context['request'].data.get('policy_holder')
            if policy_holder_id:
                try:
                    policy_holder = PolicyHolder.objects.get(pk=policy_holder_id)
                    context['policy_holder'] = policy_holder
                except PolicyHolder.DoesNotExist:
                    pass # Let serializer handle invalid ID
        return context

    @action(detail=True, methods=['post'])
    def accrue_interest(self, request, pk=None):
        loan = self.get_object()
        try:
            loan.accrue_interest()
            serializer = self.get_serializer(loan)
            return Response(serializer.data)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoanRepaymentViewSet(viewsets.ModelViewSet):
    queryset = LoanRepayment.objects.all()
    serializer_class = LoanRepaymentSerializer
    permission_classes = [IsAuthenticated] 

# --- Authentication Views ---

class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Include user type and potentially branch/agent info in response
        user_data = {
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': user.user_type,
        }
        if user.user_type == 'branch' and user.branch:
            user_data['branch_id'] = user.branch.id
            user_data['branch_name'] = user.branch.name
        elif user.user_type == 'agent' and hasattr(user, 'agent'):
             user_data['agent_id'] = user.agent.id
             # Optionally add agent name if available through relation
             # user_data['agent_name'] = user.agent.get_full_name() 

        return Response({
            'token': token.key,
            'user': user_data
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass # Handle cases where token might not exist or user isn't authenticated via token
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class HomeDataView(APIView):
 
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer_context = {'request': request} # For serializers needing request context
        
        # Fetch and serialize all data for each model
        all_data = {
            "users": UserSerializer(User.objects.all(), many=True, context=serializer_context).data,
            "occupations": OccupationSerializer(Occupation.objects.all(), many=True, context=serializer_context).data,
            "mortality_rates": MortalityRateSerializer(MortalityRate.objects.all(), many=True, context=serializer_context).data,
            "companies": CompanySerializer(Company.objects.all(), many=True, context=serializer_context).data,
            "branches": BranchSerializer(Branch.objects.all(), many=True, context=serializer_context).data,
            "insurance_policies": InsurancePolicySerializer(InsurancePolicy.objects.all(), many=True, context=serializer_context).data,
            "gsv_rates": GSVRateSerializer(GSVRate.objects.all(), many=True, context=serializer_context).data,
            "ssv_configs": SSVConfigSerializer(SSVConfig.objects.all(), many=True, context=serializer_context).data,
            "agent_applications": AgentApplicationSerializer(AgentApplication.objects.all(), many=True, context=serializer_context).data,
            "sales_agents": SalesAgentSerializer(SalesAgent.objects.all(), many=True, context=serializer_context).data,
            "duration_factors": DurationFactorSerializer(DurationFactor.objects.all(), many=True, context=serializer_context).data,
            "customers": CustomerSerializer(Customer.objects.all(), many=True, context=serializer_context).data,
            "kyc": KYCSerializer(KYC.objects.all(), many=True, context=serializer_context).data,
            "policy_holders": PolicyHolderSerializer(PolicyHolder.objects.all(), many=True, context=serializer_context).data,
            "bonus_rates": BonusRateSerializer(BonusRate.objects.all(), many=True, context=serializer_context).data,
            "bonuses": BonusSerializer(Bonus.objects.all(), many=True, context=serializer_context).data,
            "claim_requests": ClaimRequestSerializer(ClaimRequest.objects.all(), many=True, context=serializer_context).data,
            "claim_processing": ClaimProcessingSerializer(ClaimProcessing.objects.all(), many=True, context=serializer_context).data,
            "payment_processing": PaymentProcessingSerializer(PaymentProcessing.objects.all(), many=True, context=serializer_context).data,
            "underwriting": UnderwritingSerializer(Underwriting.objects.all(), many=True, context=serializer_context).data,
            "premium_payments": PremiumPaymentSerializer(PremiumPayment.objects.all(), many=True, context=serializer_context).data,
            "agent_reports": AgentReportSerializer(AgentReport.objects.all(), many=True, context=serializer_context).data,
            "loans": LoanSerializer(Loan.objects.all(), many=True, context=serializer_context).data,
            "loan_repayments": LoanRepaymentSerializer(LoanRepayment.objects.all(), many=True, context=serializer_context).data,
        }

        return Response(all_data)
