from django.contrib import admin
from .models import Category,Product,ProductImage,Address,Wallet

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Address)
admin.site.register(Wallet)