from django.urls import path
from cartapp import views

urlpatterns = [

    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
    path("sample",views.sample,name='sample'),
    path('checkout/',views.checkout, name='checkout'),
    path('set_default_address/<int:address_id>/', views.set_default_address, name='set_default_address'),
]