
from django.urls import path
from . import views

urlpatterns = [
    
    path("",views.home,name='home'),
    path("login/",views.handlelogin,name='handlelogin'),
    path("signup/",views.signup,name='signup'),
    path('logout/',views.handlelogout,name='handlelogout'),
    path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='activate'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/',views.reset_password,name='reset_password'),
    path('password_validation/<uidb64>/<token>/', views.password_validation.as_view(), name='password_validation'),
    path('reset_password/', views.reset_password, name='reset_password'),
    
    path('product_list/', views.product_list, name='product_list'),
    path('product_detail/<int:category_id>/<int:product_id>/', views.product_detail, name='product_detail'),
 
    path('user_profile',views.user_profile,name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('search/', views.search, name='search'),
    path('add_address/',views.add_address,name='add_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('manage_address/', views.manage_address, name='manage_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    
    path('order_history/',views.order_history,name='order_history'),
    path('view_order/<int:order_id>/', views.view_order, name='view_order'),
    path('cancel_order_product/<int:order_id>/', views.cancel_order_product, name='cancel_order_product'),

    path('invoice/<int:order_id>/', views.invoice_view, name='invoice'),
    path('download_invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),

    path('my_wallet/', views.my_wallet, name='my_wallet'),
    #path('wallet_pay/<str:order_number>/', views.wallet_pay, name='wallet_pay'),
    #path('cash_on_delivery/<str:order_number>/', views.cash_on_delivery, name='cash_on_delivery'),
    path('sort_list/', views.sort_list, name='sort_list'),
    path('handle_price_range/', views.handle_price_range, name='handle_price_range'),

]