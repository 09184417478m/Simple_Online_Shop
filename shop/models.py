import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
class CustomUser(AbstractUser):
    user_id = models.UUIDField(primary_key = True,default = uuid.uuid4,editable=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    anon_user = models.BooleanField(null=False,blank=False , default=True)

    def __str__(self):
        return self.username

class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    cart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # OneToOneField
    user = models.OneToOneField(CustomUser, related_name='carts', on_delete=models.CASCADE)
    # TODO one to one 

    def __str__(self):
        return f"Cart of {self.user}"

class CartItem(models.Model):
    cart_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1 , null=False)

    def __str__(self):
        return f"{self.quantity} of {self.product} in {self.cart}"
    

class Shop(models.Model):
    track_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now , null=False)

    def __str__(self):
        return f"Shop with track ID {self.track_id}"


class Opinion(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, related_name='opinions', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='opinions', on_delete=models.CASCADE)
    comment = models.TextField(null=False)
    date_time = models.DateTimeField(default=timezone.now , null=False)


class Score(models.Model):
    score_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, related_name='scores', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='scores', on_delete=models.CASCADE)
    score = models.IntegerField(null=False)

    def __str__(self):
        return f"{self.score} for {self.product}"
    
class Track(models.Model):
    track_id = models.ForeignKey(Shop , related_name="tracks" , on_delete=models.CASCADE )
    date_time = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"Tracking {self.track_id} titled {self.title}"
    




































