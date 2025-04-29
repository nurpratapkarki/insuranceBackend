from rest_framework import status, viewsets, permissions as drf_permissions
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from insurance import permissions as custom_permissions  # Renamed to avoid conflict
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

# --- Base ViewSet for common permissions ---
# By default, require authentication. Allow safe methods (GET, HEAD, OPTIONS) for anyone.
# Admins/Staff can do anything.
class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [drf_permissions.IsAuthenticatedOrReadOnly, IsAdminUser] # Default: ReadOnly for auth users, full for admin

    def get_permissions(self):
        # More specific permissions can be set in subclasses or using action decorators
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Write operations typically require admin or specific roles
            return [IsAdminUser()] 
        # Default to IsAuthenticatedOrReadOnly for list/retrieve
        return [drf_permissions.IsAuthenticatedOrReadOnly()]

# --- Specific ViewSets ---

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [custom_permissions.IsOwnerOrAdmin] # Only owner or admin can view/edit user details

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        if user.is_superuser or user.is_staff:
            return User.objects.all()
        # Allow users to see their own profile
        return User.objects.filter(pk=user.pk)

# --- Configuration Models (Mostly Admin Controlled) ---

class OccupationViewSet(viewsets.ModelViewSet):
    queryset = Occupation.objects.all()
    serializer_class = OccupationSerializer
    permission_classes = [IsAdminUser] # Only Admin should manage occupations

class MortalityRateViewSet(viewsets.ModelViewSet):
    queryset = MortalityRate.objects.all()
    serializer_class = MortalityRateSerializer
    permission_classes = [IsAdminUser] # Only Admin should manage mortality rates

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAdminUser] # Only Admin should manage companies

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminUser] # Only Admin should manage branches

class InsurancePolicyViewSet(viewsets.ModelViewSet):
    queryset = InsurancePolicy.objects.all()
    serializer_class = InsurancePolicySerializer
    permission_classes = [IsAdminUser] # Only Admin manages base policies

class GSVRateViewSet(viewsets.ModelViewSet):
    queryset = GSVRate.objects.all()
    serializer_class = GSVRateSerializer
    permission_classes = [IsAdminUser]

class SSVConfigViewSet(viewsets.ModelViewSet):
    queryset = SSVConfig.objects.all()
    serializer_class = SSVConfigSerializer
    permission_classes = [IsAdminUser]

class DurationFactorViewSet(viewsets.ModelViewSet):
    queryset = DurationFactor.objects.all()
    serializer_class = DurationFactorSerializer
    permission_classes = [IsAdminUser]

class BonusRateViewSet(viewsets.ModelViewSet):
    queryset = BonusRate.objects.all()
    serializer_class = BonusRateSerializer
    permission_classes = [IsAdminUser]

# --- Agent Related Models ---

class AgentApplicationViewSet(viewsets.ModelViewSet):
    queryset = AgentApplication.objects.all()
    serializer_class = AgentApplicationSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Anyone can apply to be an agent
            return [AllowAny()]
        # Admins or Branch Admins can manage applications
        return [custom_permissions.IsAdminOrBranchAdmin()] 
        
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
             # Allow create action even if not authenticated
            if self.action == 'create':
                return AgentApplication.objects.none() # Return none for list/retrieve if not logged in
            return AgentApplication.objects.none()

        if user.is_superuser or user.is_staff:
            return AgentApplication.objects.all()
        if user.user_type == 'branch' and user.branch:
            # Branch admin sees applications for their branch
            return AgentApplication.objects.filter(branch=user.branch)
        return AgentApplication.objects.none() # Agents/Customers don't see applications directly


class SalesAgentViewSet(viewsets.ModelViewSet):
    queryset = SalesAgent.objects.all()
    serializer_class = SalesAgentSerializer
    permission_classes = [custom_permissions.IsAdminOrBranchAdmin] # Only Admin/Branch Admin manage agents

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return SalesAgent.objects.none()

        if user.is_superuser or user.is_staff:
            return SalesAgent.objects.all()
        if user.user_type == 'branch' and user.branch:
            # Branch admin sees agents in their branch
            return SalesAgent.objects.filter(branch=user.branch)
        # Agents might see their own profile? Add if needed.
        # if user.user_type == 'agent' and hasattr(user, 'agent'):
        #     return SalesAgent.objects.filter(pk=user.agent.pk)
        return SalesAgent.objects.none()

# --- Customer and Policy Related Models ---

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Anyone can register as a customer
            permission_classes = [AllowAny]
        elif self.action in ['list', 'retrieve']:
             # Read access: Authenticated users (filtered below), or Admin/Agent
            permission_classes = [IsAuthenticated]
        else:
            # Update/delete: Owner or Admin/Agent
            permission_classes = [custom_permissions.IsOwnerOrAdminOrAgent] 
            
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # Allow creation even when not logged in (for registration)
            if self.action == 'create': return Customer.objects.none() 
            return Customer.objects.none() # No listing/retrieval for anonymous
            
        if user.is_superuser or user.is_staff:
            return Customer.objects.all()
        if user.user_type == 'branch' and user.branch:
            # Branch admins see customers associated with their branch's policies/users
            # This might need refinement depending on exact requirements, e.g., via PolicyHolder
            return Customer.objects.filter(policies__branch=user.branch).distinct()
        if user.user_type == 'agent' and hasattr(user, 'agent'):
            # Agents see customers linked through PolicyHolder
            return Customer.objects.filter(policies__agent=user.agent).distinct()
        if user.user_type == 'customer' and hasattr(user, 'customer_profile'):
            # Customers see only themselves
            return Customer.objects.filter(user=user)
            
        return Customer.objects.none() # Default to none
    
    @action(detail=True, methods=['post'], permission_classes=[custom_permissions.IsOwnerOrAdmin])
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
    permission_classes = [custom_permissions.IsOwnerOrAdminOrAgent] # Owner, Admin, or Agent can manage KYC

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return KYC.objects.none()
            
        if user.is_superuser or user.is_staff:
            return KYC.objects.all()
        if user.user_type == 'branch' and user.branch:
            # Branch admins see KYC for customers in their branch
            return KYC.objects.filter(customer__policies__branch=user.branch).distinct()
        if user.user_type == 'agent' and hasattr(user, 'agent'):
            # Agents see KYC for their customers
            return KYC.objects.filter(customer__policies__agent=user.agent).distinct()
        if user.user_type == 'customer' and hasattr(user, 'customer_profile'):
            # Customers see only their own KYC
            return KYC.objects.filter(customer=user.customer_profile)
            
        return KYC.objects.none()


class PolicyHolderViewSet(viewsets.ModelViewSet):
    queryset = PolicyHolder.objects.all()
    serializer_class = PolicyHolderSerializer
    permission_classes = [custom_permissions.IsOwnerOrAdminOrAgent] # Owner, Admin, Agent manage policies

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return PolicyHolder.objects.none()
            
        if user.is_superuser or user.is_staff:
            return PolicyHolder.objects.all()
        if user.user_type == 'branch' and user.branch:
            # Branch admins see policies in their branch
            return PolicyHolder.objects.filter(branch=user.branch)
        if user.user_type == 'agent' and hasattr(user, 'agent'):
             # Agents see policies they are assigned to
            return PolicyHolder.objects.filter(agent=user.agent)
        if user.user_type == 'customer' and hasattr(user, 'customer_profile'):
            # Customers see only their own policies
            return PolicyHolder.objects.filter(customer=user.customer_profile)
            
        return PolicyHolder.objects.none()


class BonusViewSet(viewsets.ModelViewSet):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer
    permission_classes = [custom_permissions.IsOwnerOrAdminOrAgent] # Similar permissions to PolicyHolder

    def get_queryset(self):
        user = self.request.user
        # Filter based on the related PolicyHolder's owner/agent/branch
        # (Similar logic to PolicyHolderViewSet.get_queryset)
        if not user.is_authenticated: return Bonus.objects.none()
        if user.is_superuser or user.is_staff: return Bonus.objects.all()
        if user.user_type == 'branch' and user.branch:
            return Bonus.objects.filter(customer__policies__branch=user.branch).distinct()
        if user.user_type == 'agent' and hasattr(user, 'agent'):
            return Bonus.objects.filter(customer__policies__agent=user.agent).distinct()
        if user.user_type == 'customer' and hasattr(user, 'customer_profile'):
            return Bonus.objects.filter(customer=user.customer_profile)
        return Bonus.objects.none()

class ClaimRequestViewSet(viewsets.ModelViewSet):
    queryset = ClaimRequest.objects.all()
    serializer_class = ClaimRequestSerializer
    permission_classes = [custom_permissions.IsOwnerOrAdminOrAgent] # Owner/Admin/Agent can create/view claims

    def get_queryset(self):
        user = self.request.user
        # Filter based on the related PolicyHolder's owner/agent/branch
        if not user.is_authenticated: return ClaimRequest.objects.none()
        if user.is_superuser or user.is_staff: return ClaimRequest.objects.all()
        if user.user_type == 'branch' and user.branch:
            return ClaimRequest.objects.filter(branch=user.branch)
        if user.user_type == 'agent' and hasattr(user, 'agent'):
             # Agents might view claims for policies they manage
            return ClaimRequest.objects.filter(policy_holder__agent=user.agent)
        if user.user_type == 'customer' and hasattr(user, 'customer_profile'):
            # Customers see only their own claims
            return ClaimRequest.objects.filter(policy_holder__customer=user.customer_profile)
        return ClaimRequest.objects.none()

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
    permission_classes = [custom_permissions.IsAdminOrBranchAdmin] # Only Admin/Branch Admin process claims

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated: return ClaimProcessing.objects.none()
        if user.is_superuser or user.is_staff: return ClaimProcessing.objects.all()
        if user.user_type == 'branch' and user.branch:
            return ClaimProcessing.objects.filter(branch=user.branch)
        return ClaimProcessing.objects.none()

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
    permission_classes = [custom_permissions.IsAdminOrBranchAdmin] # Only Admin/Branch Admin handle payments

    def get_queryset(self):
        user = self.request.user
        # Filter similar to ClaimProcessing
        if not user.is_authenticated: return PaymentProcessing.objects.none()
        if user.is_superuser or user.is_staff: return PaymentProcessing.objects.all()
        if user.user_type == 'branch' and user.branch:
            return PaymentProcessing.objects.filter(branch=user.branch)
        return PaymentProcessing.objects.none()
        
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
    permission_classes = [custom_permissions.IsAdminOrBranchAdmin] # Admin/Branch Admin manage underwriting

    def get_queryset(self):
        user = self.request.user
        # Filter based on related policy holder's branch
        if not user.is_authenticated: return Underwriting.objects.none()
        if user.is_superuser or user.is_staff: return Underwriting.objects.all()
        if user.user_type == 'branch' and user.branch:
            return Underwriting.objects.filter(policy_holder__branch=user.branch)
        return Underwriting.objects.none()

class PremiumPaymentViewSet(viewsets.ModelViewSet):
    queryset = PremiumPayment.objects.all()
    serializer_class = PremiumPaymentSerializer
    permission_classes = [custom_permissions.IsOwnerOrAdminOrAgent] # Customer can view, Admin/Agent can manage

    def get_queryset(self):
        user = self.request.user
        # Filter based on the related PolicyHolder's owner/agent/branch
        if not user.is_authenticated: return PremiumPayment.objects.none()
        if user.is_superuser or user.is_staff: return PremiumPayment.objects.all()
        if user.user_type == 'branch' and user.branch:
            return PremiumPayment.objects.filter(policy_holder__branch=user.branch)
        if user.user_type == 'agent' and hasattr(user, 'agent'):
            return PremiumPayment.objects.filter(policy_holder__agent=user.agent)
        if user.user_type == 'customer' and hasattr(user, 'customer_profile'):
            return PremiumPayment.objects.filter(policy_holder__customer=user.customer_profile)
        return PremiumPayment.objects.none()

class AgentReportViewSet(viewsets.ModelViewSet):
    queryset = AgentReport.objects.all()
    serializer_class = AgentReportSerializer
    permission_classes = [custom_permissions.IsAdminOrBranchAdmin] # Only Admin/Branch Admin manage agent reports

    def get_queryset(self):
        user = self.request.user
        # Filter similar to SalesAgent
        if not user.is_authenticated: return AgentReport.objects.none()
        if user.is_superuser or user.is_staff: return AgentReport.objects.all()
        if user.user_type == 'branch' and user.branch:
            return AgentReport.objects.filter(branch=user.branch)
        # if user.user_type == 'agent' and hasattr(user, 'agent'):
        #     return AgentReport.objects.filter(agent=user.agent) # Agent sees their own reports
        return AgentReport.objects.none()


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [custom_permissions.IsOwnerOrAdminOrAgent] # Customer/Admin/Agent access loans

    def get_queryset(self):
        user = self.request.user
        # Filter based on the related PolicyHolder
        if not user.is_authenticated: return Loan.objects.none()
        if user.is_superuser or user.is_staff: return Loan.objects.all()
        if user.user_type == 'branch' and user.branch:
            return Loan.objects.filter(policy_holder__branch=user.branch)
        if user.user_type == 'agent' and hasattr(user, 'agent'):
            return Loan.objects.filter(policy_holder__agent=user.agent)
        if user.user_type == 'customer' and hasattr(user, 'customer_profile'):
            return Loan.objects.filter(policy_holder__customer=user.customer_profile)
        return Loan.objects.none()

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
    permission_classes = [custom_permissions.IsOwnerOrAdminOrAgent] # Customer/Admin/Agent can make/view repayments

    def get_queryset(self):
        user = self.request.user
        # Filter based on the related Loan's PolicyHolder
        if not user.is_authenticated: return LoanRepayment.objects.none()
        if user.is_superuser or user.is_staff: return LoanRepayment.objects.all()
        if user.user_type == 'branch' and user.branch:
            return LoanRepayment.objects.filter(loan__policy_holder__branch=user.branch)
        if user.user_type == 'agent' and hasattr(user, 'agent'):
            return LoanRepayment.objects.filter(loan__policy_holder__agent=user.agent)
        if user.user_type == 'customer' and hasattr(user, 'customer_profile'):
            return LoanRepayment.objects.filter(loan__policy_holder__customer=user.customer_profile)
        return LoanRepayment.objects.none()

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