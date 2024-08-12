from rest_framework.permissions import BasePermission

from shop.models import Shop

class IsNotAnonUser(BasePermission):

    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False
      
        has_purchased = Shop.objects.filter(cart__user=request.user).exists()
        
        return has_purchased
