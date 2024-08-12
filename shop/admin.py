from rest_framework.authtoken.models import Token
from django.contrib import admin
from shop.models import CustomUser,Product,Cart,CartItem,Shop,Opinion,Score,Track

class customUser(admin.ModelAdmin):
    list_display = ('username','user_id', 'phone_number', 'image', 'anon_user','is_superuser','is_staff')

class product(admin.ModelAdmin):
    list_display = ('product_id', 'type', 'name', 'brand')

class opinion(admin.ModelAdmin):
    list_display = ('user', 'comment_id', 'product')
class shop(admin.ModelAdmin):
    list_display = ('track_id', 'cart')

class track(admin.ModelAdmin):
    list_display = ('id' , 'track_id')
      

admin.site.register(CustomUser,customUser)
admin.site.register(Product,product)
admin.site.register(Token)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Shop,shop)
admin.site.register(Opinion,opinion)
admin.site.register(Score)
admin.site.register(Track,track)























