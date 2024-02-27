from django.urls import path
from . import views
from django.urls import include, path
#app_name = 'orderapp'

urlpatterns = [
    # path('add_billing_address/', views.add_billing_address, name='add_billing_address'),
    path('place_order/', views.place_order, name='place_order'),
    path('payments/<int:order_id>/', views.payments, name='payments'),
    #path('payments/<str:order_number>/', views.payments, name='payments'),
    path('order_confirmed/<str:order_number>/', views.order_confirmed, name='order_confirmed'),
    #path('payments/<int:order_id>/', views.payments, name='payments'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('cash_on_delivery/<str:order_number>/', views.cash_on_delivery, name='cash_on_delivery'),
    #path('available_coupons/<str:order_number>/', views.available_coupons, name='available_coupons'),
    path('order_confirmed/<int:order_number>/', views.order_confirmed, name='order_confirmed'),
    path('confirm_razorpay_payment/<str:order_number>/', views.confirm_razorpay_payment, name='confirm_razorpay_payment'),
    path('mycoupons/', views.mycoupons, name='mycoupons'),

    path('wallet_pay/<int:order_id>/', views.wallet_pay, name='wallet_pay'),

    path('check_cod_eligibility/<str:order_number>/', views.check_cod_eligibility, name='check_cod_eligibility'),
]