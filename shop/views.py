from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import status,generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
import rest_framework_simplejwt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.paginator import PageNotAnInteger,EmptyPage,Paginator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from shop.models import Cart, CartItem, Opinion, Product, Score, Shop, Track
from django.db.models import Avg
from shop.exceptions import ValueError, NotFound
from shop.permissionclasses import IsNotAnonUser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from shop.serializers import (
    AverageScoreSerializer,
    CartItemInputSerializer,
    CartRemoveInputSerializer,
    Opinion_add_Serializer,
    Opinion_list_Serializer,
    ProductSerializer,
    ProductsWrapperSerializer,
    RegisterSerializer,
    LoginSerializer,
    ScoreSerializer,
    ShopSerializer,
    TokenResponseSerializer,
    TrackSerializer,
    UserSerializer,
    ChangePasswordSerializer
)



User = get_user_model()

@extend_schema(
    request=RegisterSerializer,
    responses={201: dict(message="User registered successfully")}
)

class RegisterView(APIView):
    permission_classes=[]
    authentication_classes=[]
       
    def post(self, request, *args, **kwargs):
            
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            Cart.objects.create(user=user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
    
        
@extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(response=TokenResponseSerializer, description='Token response'),
            404: OpenApiResponse(response=None, description='user not found'),
            406:OpenApiResponse(response=None , description='Bad request')
        }
    )

class LoginView(APIView):

    permission_classes=[]
    authentication_classes=[]

    def post(self, request, *args, **kwargs):
            
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            raise ValueError("invalid credentials")
          
      

@extend_schema(
    responses={
        205: None,
        401: OpenApiResponse(response=None, description='Unauthorized'),
        406: OpenApiResponse(response=None, description='Invalid or expired refresh token'),
    },
    parameters=[
        OpenApiParameter(name='Refresh-Token', description='Refresh token for blacklisting', required=True, type=str, location=OpenApiParameter.HEADER),
    ],
)

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise ValueError('invalid input')

            access_token = auth_header.split(' ')[1]
   
            try:
               
                refresh_token = request.headers.get('Refresh-Token')  
                if not refresh_token:
                    raise ValueError('refresh token is not given')

                token = RefreshToken(refresh_token)
                token.blacklist()

                return Response(status=status.HTTP_205_RESET_CONTENT)
            except rest_framework_simplejwt.exceptions.TokenError as e:
                raise ValueError('error with token')

        
@extend_schema(
        request=None,  
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description='Users personal information'
            ),
            401: OpenApiResponse(
                response=None,
                description='Unauthorized access'
            ),
            500: OpenApiResponse(
                response=None,
                description='Server error'
            ),
        },
    )
class UserProfileView(APIView):
   
    permission_classes= [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.data)
        return Response(serializer.data)


@extend_schema(
        request=UserSerializer,  
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description='User profile updated successfully'
            ),
            400: OpenApiResponse(
                response=None,
                description='Bad request due to invalid data'
            ),
            401: OpenApiResponse(
                response=None,
                description='Unauthorized access'
            ),
            500: OpenApiResponse(
                response=None,
                description='Server error'
            ),
        },
       
    )
class UpdateProfileView(APIView):
   
    permission_classes= [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
       

@extend_schema(
        request=ChangePasswordSerializer, 
        responses={
            200: OpenApiResponse(
                response=None, 
                description='Password changed successfully. Returns new access and refresh tokens.'
            ),
            400: OpenApiResponse(
                response=None,
                description='Bad request due to invalid data or mismatched passwords.'
            ),
            401: OpenApiResponse(
                response=None,
                description='Unauthorized access due to incorrect old password.'
            ),
            500: OpenApiResponse(
                response=None,
                description='Server error'
            ),
        },
        
    )
class ChangePasswordView(APIView):

    permission_classes= [IsAuthenticated]

    def post(self, request, *args, **kwargs):
            
            serializer = ChangePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = request.user

            if not user.check_password(serializer.validated_data['old_password']):
                 raise ValueError("old password is wrong")
            
            
            if serializer.validated_data['new_password'] == serializer.validated_data['old_password']:
                 raise ValueError("new password and old password must not be same")

            
            if serializer.validated_data['new_password'] != serializer.validated_data['new_password_repeat']:
                raise ValueError("new password repeat did not match  new password")
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
    


@extend_schema(
        parameters=[
            OpenApiParameter(name='type', description='Filter by product type',  type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='name', description='Filter by product name',  type=str, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='brand', description='Filter by product brand', type=str, location=OpenApiParameter.QUERY),
            
        ],
        responses={
            200: OpenApiResponse(
                response=ProductSerializer(many=True),
                description='List of products with the specified filters and search terms applied.'
            ),
            400: OpenApiResponse(
                response=None,
                description='Bad request due to invalid parameters or filter values.'
            ),
        }
    )
class ProductListView(generics.ListAPIView):

    authentication_classes=[]
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['type', 'name', 'brand']
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
         
        if self.request.query_params.get('type'):
            type_param = self.request.query_params.get('type').lower()
            queryset = queryset.filter(type__iexact=type_param)

        if self.request.query_params.get('name'):
            name_param = self.request.query_params.get('name').lower()
            queryset = queryset.filter(name__iexact=name_param)

        if self.request.query_params.get('brand'):
            brand_param = self.request.query_params.get('brand').lower()
            queryset = queryset.filter(brand__iexact=brand_param)
             

        return queryset

 

@extend_schema(
        parameters=[
            OpenApiParameter(name='product_id', description='ID of the product to retrieve', required=True, type=str, location=OpenApiParameter.PATH),
        ],
        responses={
            200: OpenApiResponse(
                response=ProductSerializer,
                description='Details of the requested product.'
            ),
            404: OpenApiResponse(
                response=None,
                description='Product not found.'
            ),
        }
    )
class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self,request ,product_id, *args, **kwargs):
        try:

            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            raise NotFound("product not found")
            

        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    
@extend_schema(
        request=ProductsWrapperSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Successfully removed items from the cart.'
            ),
            400: OpenApiResponse(
                response=None,
                description='Bad request, validation errors.'
            ),
            404: OpenApiResponse(
                response=None,
                description='Product or Cart item not found.'
            ),
        }
    )
       
class CartAddView(APIView):

    permission_classes= [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):

        cart = Cart.objects.get(user=request.user)
        serializer = CartItemInputSerializer(data=request.data.get('products', []), many=True)
        serializer.is_valid(raise_exception=True)

        response_data = []

        for item in serializer.validated_data:
            product_id = item.get('id')
            quantity = item.get('quantity')
            try:
                product = Product.objects.get(product_id=product_id)
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                if not created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = quantity
                cart_item.save()
                response_data.append({"id": product_id, "success": True, "message": "Added to cart"})
            except Product.DoesNotExist:
                response_data.append({"id": product_id, "success": False, "message": "Product not found"})

        return Response(response_data, status=status.HTTP_200_OK)

@extend_schema(
      request=CartRemoveInputSerializer,
        responses={
            200: OpenApiResponse(
                response=None,  
                description='Successfully removed items from the cart.'
            ),
            400: OpenApiResponse(
                response=None,
                description='Bad request, validation errors.'
            ),
        },
         parameters=[
            OpenApiParameter(name='Authorization', description='Bearer token for authentication', required=False, type=str, location=OpenApiParameter.HEADER)
        ]
    )
class CartRemoveView(APIView):

    permission_classes= [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)

        if request.data.get('product_ids') == 'all':
            cart.items.all().delete()
            return Response({"detail": "Cart emptied successfully."}, status=status.HTTP_200_OK)
        
        serializer = CartRemoveInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_ids = serializer.validated_data.get('product_ids', [])
        response_data = []
      
     

        for product_id in product_ids:
            try:
                product = Product.objects.get(product_id=product_id)
                cart_item = CartItem.objects.get(cart=cart, product=product)
                cart_item.delete()
                response_data.append({"id": product_id, "success": True, "message": "Removed from cart"})
            except Product.DoesNotExist:
                response_data.append({"id": product_id, "success": False, "message": "Product not found"})
            except CartItem.DoesNotExist:
                response_data.append({"id": product_id, "success": False, "message": "Product not in cart"})

        return Response(response_data, status=status.HTTP_200_OK)
    

@extend_schema(
        request=None, 
        responses={
            201: OpenApiResponse(
                response=ShopSerializer,
                description='Shop created successfully with track_id and date_time.'
            ),
            200: OpenApiResponse(
                response=dict,
                description='Cart was empty, no shop created.'
            ),
            400: OpenApiResponse(
                response=None,
                description='Bad request, validation errors.'
            ),
        }
    )
class ShopView(APIView):

    permission_classes= [IsAuthenticated]
 
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        shop = Shop.objects.create(cart=cart)
        
        if CartItem.objects.filter(cart=cart):
            CartItem.objects.filter(cart=cart).delete()
         
        else :
            return Response({"error":"cart is empty"}, status=status.HTTP_200_OK)


        serializer = ShopSerializer(shop)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

@extend_schema(
        request=Opinion_add_Serializer,
        responses={
            201: OpenApiResponse(
                response=OpenApiResponse(
                    response=dict,
                    description='Opinion added successfully.'
                )
            ),
            404: OpenApiResponse(
                response=dict,
                description='Product not found.'
            ),
            406: OpenApiResponse(
                response=dict,
                description='User not allowed to add comment because they have not bought any product.'
            ),
        }
    )
class OpinionAddView(APIView):
    
    permission_classes= [IsAuthenticated, IsNotAnonUser]
     
    def post(self, request, product_id, *args, **kwargs):
              
        try:
            product = Product.objects.get(product_id=product_id)
                     
        except Product.DoesNotExist:
            raise NotFound("product not found")
              
        serializer = Opinion_add_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save(user = request.user , product = product)
        return Response({"detail": "Opinion added successfully."}, status=status.HTTP_201_CREATED)

    

    
@extend_schema(
    parameters=[
 
        OpenApiParameter(name='search', description='Search term for filtering opinions by comment or date_time', required=False, type=str, location=OpenApiParameter.QUERY),
    ],
    responses={
        200: OpenApiResponse(
            response=Opinion_list_Serializer(many=True),
            description='List of opinions with optional filtering and search.'
        ),
        400: OpenApiResponse(
                response=None,
                description='Bad request due to invalid parameters or filter values.'
            ),
    }
)
class OpinionListView(generics.ListAPIView):
    queryset = Opinion.objects.all()
    serializer_class = Opinion_list_Serializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['comment', 'date_time']

 
@extend_schema(
        request=ScoreSerializer,
        responses={
            201: OpenApiResponse(
                response=ScoreSerializer,
                description='Score added successfully'
            ),
            400: OpenApiResponse(
                response=None,
                description='Bad request - Score already exists or invalid data'
            ),
            404: OpenApiResponse(
                response=None,
                description='Product not found'
            ),
        }
    )
   
class ScoreAddView(APIView):

    permission_classes= [IsAuthenticated, IsNotAnonUser]

    def post(self, request, product_id, *args, **kwargs):
        
        
        user = User.objects.get(user_id=request.user.user_id)
    
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            raise NotFound("product not found")

        
        if Score.objects.filter(product=product, user=user).exists():
           raise ValueError("You have already scored this product.")
         
       
        serializer = ScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user = request.user , product = product)
        return Response({"detail": "Score added successfully."}, status=status.HTTP_201_CREATED)



@extend_schema(
        responses={
            200: OpenApiResponse(
                response=AverageScoreSerializer,
                description='Average score of the product.'
            ),
            404: OpenApiResponse(
                response=None,
                description='Product not found.'
            ),
        }
    )      

class ScoreGetView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id, *args, **kwargs):
        

        scores = Score.objects.filter(product_id=product_id)
        
        if scores.exists():
            avg_score = scores.aggregate(Avg('score'))['score__avg']
        else:
            avg_score = 0

        serializer = AverageScoreSerializer({"average_score": avg_score})
        return Response(serializer.data,status=status.HTTP_200_OK)
    


    

@extend_schema(
    responses={
        200: OpenApiResponse(
            response=TrackSerializer(many=True),
            description='A paginated list of tracking codes.'
        )
    }
)

class TrackListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsNotAnonUser]
    serializer_class = TrackSerializer

    def get_queryset(self):
        user = self.request.user
        return Track.objects.filter(track_id__cart__user=user)

    
@extend_schema(
        responses={
            200: OpenApiResponse(
                response=TrackSerializer,
                description='Details of the tracking code.'
            ),
            404: OpenApiResponse(
                response=None,
                description='Tracking code not found.'
            ),
        }
    )


class TrackDetailView(APIView):
    permission_classes = [IsAuthenticated, IsNotAnonUser]

    def get(self, request, track_id, *args, **kwargs):
        try:
            track = Track.objects.get(track_id=track_id, track_id__cart__user=request.user)

        except Track.DoesNotExist:
            raise NotFound("track not found")
        
        serializer = TrackSerializer(track)
        return Response(serializer.data)
    

