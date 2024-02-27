from django.db import models
from django.contrib.auth.models import User
# Model to create category
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    category_images = models.ImageField(upload_to='photos/categories', blank=True)
    is_available = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    #slug         =models.SlugField(max_length=200,unique=True)
    description  =models.TextField(max_length=500,blank=True)
    original_price=models.IntegerField()
    selling_price =models.IntegerField()
    product_images = models.ImageField(upload_to='photos/product', default='default_image.jpeg')
    quantity  = models.IntegerField()
    is_available = models.BooleanField(default=True)
    soft_deleted = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    

    def __str__(self):
        return self.product_name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='photos/product', default='default_image.jpeg')

    def __str__(self):
        return f"Image of {self.product.product_name}"           


#Varient model
class VariantManager(models.Manager):
    def colors(self):
        return super(VariantManager, self).filter(variant_category = 'color', is_active = True)

    def sizes(self):
        return super(VariantManager, self).filter(variant_category = 'size', is_active = True)

variant_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
    )

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant_category = models.CharField(max_length=100, choices=variant_category_choice)
    variant_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now=True)

    objects = VariantManager()

    def __str__(self):
        return self.variant_value





class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=20, default='')
    phone = models.CharField(max_length=15)
    email=models.EmailField(max_length=100, unique=True)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    city = models.CharField(max_length=20)
    zipcode = models.CharField(max_length=6)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet for {self.user.first_name}"