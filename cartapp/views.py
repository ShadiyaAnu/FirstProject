from django.shortcuts import render
from django.shortcuts import render,redirect
from userapp.models import Product,Address
from cartapp.models import Cart, CartItem

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F

# Create your views here.
def sample(request):
    return render(request, 'user/cartnew.html')



def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


from django.http import JsonResponse

def add_carts(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:
        cart_item = CartItem.objects.filter(product=product, user=current_user).first()
        if cart_item:
            if cart_item.quantity < product.quantity:
                cart_item.quantity += 1
                cart_item.save()
                return redirect('cart')
                
            else:
                messages.warning(request, 'Product quantity in cart exceeds available quantity.')
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            
        messages.success(request, 'Product Added to Cart')
            
        return redirect('cart')
    
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        cart_item = CartItem.objects.filter(product=product, cart=cart).first()
        if cart_item:
            if cart_item.quantity < product.quantity:
                cart_item.quantity += 1
                cart_item.save()
                return redirect('cart')
            else:
                messages.warning(request, 'Product quantity in cart exceeds available quantity.')
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
        messages.success(request, 'Product Added to Cart')

    # Construct JSON response
    return JsonResponse({
        'quantity': cart_item.quantity,
        'item_total': cart_item.sub_total,
        'sub_total': total,  # Update this with your actual subtotal
        'grand_total': grand_total,  # Update this with your actual grand total
    })

def remove_carts(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(product=product, user=request.user).first()
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.filter(product=product, cart=cart).first()
        
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    except ObjectDoesNotExist:
        pass

    return JsonResponse({
        'quantity': cart_item.quantity if cart_item else 0,
        'item_total': cart_item.sub_total if cart_item else 0,
        #'sub_total': total,  # Update this with your actual subtotal
        #'grand_total': grand_total,  # Update this with your actual grand total
    })   



def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:
        cart_item = CartItem.objects.filter(product=product, user=current_user).first()
        if cart_item:
            if cart_item.quantity < product.quantity:
                cart_item.quantity += 1
                cart_item.save()
                return redirect('cart')
                
            else:
                messages.warning(request, 'Product quantity in cart exceeds available quantity.')
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            
        messages.success(request, 'Product Added to Cart')
            
        return redirect('cart')
    
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        cart_item = CartItem.objects.filter(product=product, cart=cart).first()
        if cart_item:
            if cart_item.quantity < product.quantity:
                cart_item.quantity += 1
                cart_item.save()
                return redirect('cart')
            else:
                messages.warning(request, 'Product quantity in cart exceeds available quantity.')
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
        messages.success(request, 'Product Added to Cart')
        return redirect('cart')






def remove_cart(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(product=product, user=request.user).first()
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.filter(product=product, cart=cart).first()
        
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    except ObjectDoesNotExist:
        pass

    return redirect('cart')


def remove_cart_item(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(product=product, cart=cart)
    
    if cart_items.exists():
        cart_item_to_delete = cart_items.first()
        cart_item_to_delete.delete()
    
    return redirect('cart')






@login_required(login_url='handlelogin')
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        shipping = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.original_price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        shipping = (100 * quantity)
        grand_total = total + tax + shipping
        grand_total = round(grand_total, 2)
    except Cart.DoesNotExist:
        pass
    except CartItem.DoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'shipping': shipping,
        'grand_total': grand_total,
    }
    return render(request,'user/cart.html', context)




@login_required(login_url='handlelogin')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        shipping = 0
        grand_total = 0
      

        if request.user.is_authenticated:
            user_id = request.user.id
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)


        for cart_item in cart_items:
            total += (cart_item.product.original_price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        
        shipping = (100 * quantity)
        grand_total = total + tax + shipping
        grand_total = round(grand_total, 2)


    except Cart.DoesNotExist:
        pass
    except CartItem.DoesNotExist:
        pass

    
    unavailable_items = cart_items.filter(product__quantity__lt=F('quantity'))
    if unavailable_items.exists():
        messages.warning(request, 'Some products in your cart are not available in sufficient quantity. Please remove them or update quantities.')
        return redirect('cart') 
    

    current_user = request.user
    address_list = Address.objects.filter(user=current_user)    
    default_address = address_list.filter(is_default=True).first()

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'shipping':shipping,
        'grand_total': grand_total,
        'address_list': address_list,
        'default_address': default_address,
       
       
    }
    return render(request, 'user/checkout.html', context)    


@login_required
def set_default_address(request, address_id):
    addr_list = Address.objects.filter(user=request.user)
    for a in addr_list:
        a.is_default = False
        a.save()
    address = Address.objects.get(id=address_id)
    address.is_default=True
    address.save()
    return redirect('checkout')