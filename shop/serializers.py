# shop/serializers.py

from datetime import datetime
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from shop.models import Cart, CartItem, Opinion, Product, Score, Shop, Track


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'password', 'email', 'first_name', 'last_name', 'phone_number', 'image')
        extra_kwargs = {
            'user_id': {'read_only': True},
            'username': {'required': True},
            'password': {'required': True, 'write_only': True},
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
            'image': {'required': False},
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number'),
            image=validated_data.get('image')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()



class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id','username', 'email', 'first_name', 'last_name', 'phone_number', 'image')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_repeat = serializers.CharField(required=True)

    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('product_id', 'type', 'name', 'brand')

class CartItemInputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)



class ProductsWrapperSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=CartItemInputSerializer()
    )



class CartRemoveInputSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.UUIDField(), 
        allow_empty=True,
        required=True
    )
   

class ShopSerializer(serializers.ModelSerializer):
    date_time = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ('track_id', 'date_time')

    def get_date_time(self, obj):
        return obj.date_time.strftime("%Y-%m-%d %H:%M:%S")
    
class Opinion_add_Serializer(serializers.ModelSerializer):
    date_time = serializers.SerializerMethodField()
    comment = serializers.CharField(max_length=500)

    class Meta:
        model = Opinion
        fields = ('comment_id', 'product', 'user', 'comment', 'date_time')
        extra_kwargs = {
            'product': {'read_only': True},
            'user' : {'read_only':True}
        }

    def get_date_time(self, obj):
        return int(obj.date_time.timestamp())



    
class Opinion_list_Serializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Opinion
        fields = ('comment', 'date_time')


class ScoreSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    score = serializers.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = Score
        fields = ('score_id', 'product', 'user', 'score')
        extra_kwargs = {
            'product': {'read_only': True}
        }

   
    

class AverageScoreSerializer(serializers.Serializer):
    average_score = serializers.FloatField()

class TrackSerializer(serializers.ModelSerializer):
    date_time = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = ('track_id', 'date_time', 'title')

    def get_date_time(self, obj):
        return obj.date_time.strftime("%Y-%m-%d %H:%M:%S")  