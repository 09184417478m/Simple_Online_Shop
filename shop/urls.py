# shop/urls.py

from django.urls import path
from shop.views import (
    CartAddView,
    CartRemoveView,
    OpinionAddView,
    OpinionListView,
    ProductDetailView,
    ProductListView,
    RegisterView,
    LoginView,
    LogoutView,
    ScoreAddView,
    ScoreGetView,
    ShopView,
    TrackDetailView,
    TrackListView,
    UserProfileView,
    UpdateProfileView,
    ChangePasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('get-profile/', UserProfileView.as_view(), name='get_profile'),
    path('set-profile/', UpdateProfileView.as_view(), name='set_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('product/list/', ProductListView.as_view(), name='product_list'),
    path('product/get/<uuid:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/add/', CartAddView.as_view(), name='cart_add'),
    path('cart/remove/', CartRemoveView.as_view(), name='cart_remove'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('opinion/add/<uuid:product_id>/', OpinionAddView.as_view(), name='opinion_add'),
    path('opinion/list/<uuid:product_id>/', OpinionListView.as_view(), name='opinion_list'),
    path('score/add/<uuid:product_id>/', ScoreAddView.as_view(), name='score_add'),
    path('score/get/<uuid:product_id>/', ScoreGetView.as_view(), name='score_get'),
    path('track/list/', TrackListView.as_view(), name='tracking_code_list'),
    path('track/get/<uuid:track_id>/', TrackDetailView.as_view(), name='tracking_code_detail'),

]
