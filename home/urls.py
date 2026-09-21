from django.urls import path
from . import views

urlpatterns = [
    # 🔐 AUTH
    path('', views.login_view, name='login'),

    path('home/', views.home, name='home'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),

    # 🏠 HOME
    

    # 👤 PROFILE
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    # 📍 ADDRESS
    path('add-address/', views.add_address, name='add_address'),
  
    path('helpcenter/',views.help,name="help"),
    path('faq/',views.faq,name="faq"),
 

    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-wishlist/<int:pid>/', views.add_to_wishlist, name='add_to_wishlist'),

    path('orders/', views.orders, name='orders'),
    path('place-order/', views.place_order, name='place_order'),

    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:pid>/', views.add_to_cart, name='add_to_cart'),

    path('cart/increase/<int:cid>/', views.increase_qty, name='increase_qty'),
    path('cart/decrease/<int:cid>/', views.decrease_qty, name='decrease_qty'),
    path('cart/remove/<int:cid>/', views.remove_cart, name='remove_cart'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),

    path('remove-wishlist/<int:wid>/', views.remove_wishlist, name='remove_wishlist'),
    path('move-to-cart/<int:wid>/', views.move_to_cart, name='move_to_cart'),



]
