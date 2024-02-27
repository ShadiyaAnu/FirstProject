from django.contrib import admin
from .models import OrderProduct,Order,Payment

admin.site.register(OrderProduct)
admin.site.register(Order)
admin.site.register(Payment)
