from rest_framework import permissions
from .models import User, Customer, PolicyHolder, SalesAgent # Import necessary models

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows read-only access to any user, but write access only to admin users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsAdminOrBranchAdmin(permissions.BasePermission):
    """
    Allows access only to admin users or users who are branch admins.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.user_type == 'branch')
        )

class IsAdminOrAgent(permissions.BasePermission):
    """
    Allows access only to admin users or users who are sales agents.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.user_type == 'agent')
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    Assumes the view is for a model directly linked to a User (e.g., User profile itself)
    or has a 'user' or 'customer' field linking back to the user.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user and request.user.is_staff:
            return True

        # Check ownership based on common patterns
        if hasattr(obj, 'user'):
            # Direct user link (e.g., User model itself, potentially Customer)
            return obj.user == request.user
        if hasattr(obj, 'customer') and hasattr(obj.customer, 'user'):
            # Objects linked via Customer (e.g., KYC, PolicyHolder)
            return obj.customer.user == request.user
        
        # Fallback for direct User object check (e.g., UserViewSet)
        if isinstance(obj, User):
            return obj == request.user
            
        return False

class IsOwnerOrAdminOrAgent(permissions.BasePermission):
    """
    Custom permission allowing:
    - Admins (staff/superuser)
    - The owner of the object (via customer.user)
    - An agent associated with the object (via policy_holder.agent)
    """
    def has_object_permission(self, request, view, obj):
        # Admins always have access
        if request.user and request.user.is_staff:
            return True
            
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        is_owner = False
        is_related_agent = False

        # Check for customer ownership
        customer_user = None
        if hasattr(obj, 'customer') and hasattr(obj.customer, 'user'):
            customer_user = obj.customer.user
        elif hasattr(obj, 'policy_holder') and hasattr(obj.policy_holder, 'customer') and hasattr(obj.policy_holder.customer, 'user'):
            customer_user = obj.policy_holder.customer.user
        elif hasattr(obj, 'loan') and hasattr(obj.loan, 'policy_holder') and hasattr(obj.loan.policy_holder, 'customer') and hasattr(obj.loan.policy_holder.customer, 'user'): # For LoanRepayment
             customer_user = obj.loan.policy_holder.customer.user
        elif isinstance(obj, Customer) and hasattr(obj, 'user'): # Direct Customer object
            customer_user = obj.user
            
        if customer_user == request.user:
            is_owner = True

        # Check if the user is the agent related to the object (usually via PolicyHolder)
        agent = None
        if hasattr(obj, 'policy_holder') and hasattr(obj.policy_holder, 'agent'):
             agent = obj.policy_holder.agent
        elif hasattr(obj, 'loan') and hasattr(obj.loan, 'policy_holder') and hasattr(obj.loan.policy_holder, 'agent'): # For LoanRepayment
             agent = obj.loan.policy_holder.agent
        # Add other ways an agent might be linked if necessary
        
        if request.user.user_type == 'agent' and hasattr(request.user, 'agent') and agent == request.user.agent:
            is_related_agent = True

        return is_owner or is_related_agent

# Add AllowAny explicitly if needed elsewhere, though usually imported from rest_framework.permissions
# from rest_framework.permissions import AllowAny

class UserTypePermission(permissions.BasePermission):
    """
    Permission class that restricts access based on user_type
    """
    allowed_user_types = []  # Override this in subclasses
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Staff/superusers can do anything
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        # Check if user's type is in the allowed types
        return request.user.user_type in self.allowed_user_types

# Example subclasses
class IsAdminOrBranchAdmin(UserTypePermission):
    allowed_user_types = ['superadmin', 'branch']
    
class IsAdminOrAgent(UserTypePermission):
    allowed_user_types = ['superadmin', 'branch', 'agent']