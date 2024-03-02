from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Order, OrderProduct, Payment
from cartapp.models import CartItem,Coupons,UserCoupons
from  userapp.models import Product,Address,Wallet
import datetime
from django.contrib import messages
import uuid
from django.utils import timezone
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db.models import F
from django.contrib.auth.decorators import login_required
#@transaction.atomic

#@transaction.atomic
# views.py

from django.http import JsonResponse

def check_cod_eligibility(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        if order.order_total > 1000:
            return JsonResponse({'eligible': False})
        else:
            return JsonResponse({'eligible': True})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)



def cash_on_delivery(request, order_number):
    current_user = request.user
    try:
        order = Order.objects.get(order_number=order_number, user=current_user, is_ordered=False)
    except Order.DoesNotExist:
        order = get_object_or_404(Order, order_number=order_number, user=current_user, is_ordered=True)
    
    total_amount = order.order_total 
    
    # Check if the total amount is less than or equal to zero
    if total_amount <= 1000:
        # Proceed with cash on delivery
        payment_method = "Cash On Delivery"
        status = "Not Paid"
    else:
        # Redirect or show an error message indicating that COD is not available
        #return HttpResponse("Cash on Delivery is not available for orders with a total amount greater than 1000.")
        messages.warning(request, 'Cash on Delivery is not available for orders with a total amount greater than 1000.')
        return redirect('payments', order_id=order_number)
    
    # Create payment object
    payment = Payment(user=current_user, payment_method=payment_method, amount_paid=total_amount, status=status)
    payment.save()
   
    # Mark order as ordered and associate with payment
    order.is_ordered = True
    order.payment = payment
    order.save()
    
    # Update product quantities and create order products
    cart_items = CartItem.objects.filter(user=current_user)
    for cart_item in cart_items:
        product = cart_item.product
        stock = product.quantity - cart_item.quantity
        product.quantity = stock
        product.save()
        order_product = OrderProduct(
            order=order,
            payment=payment,
            user=current_user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.product.original_price,
            ordered=True,
        )
        order_product.save()
    
    # Clear cart items
    cart_items.delete()
    
    context = {'order': order}
    return render(request, 'order/order_confirmed.html', context)





from django.utils import timezone
from django.shortcuts import redirect, render

def payments(request, order_id):
    current_user = request.user

    # Retrieve coupon code from session
    coupon_code = request.session.get('coupon_code')

    # Initialize coupon and discount variables
    coupon = None
    discount = 0

    # If coupon code exists, fetch the coupon object
    if coupon_code:
        try:
            coupon = Coupons.objects.get(coupon_code=coupon_code)
            print("Coupon retrieved:", coupon)  # Debug statement

            # Check if coupon is valid and applicable
            if coupon.valid_from <= timezone.now() <= coupon.valid_to:
                cart_items = CartItem.objects.filter(user=current_user)
                total = sum(cart_item.product.original_price * cart_item.quantity for cart_item in cart_items)
                if total >= coupon.minimum_amount:
                    discount = coupon.discount
                    print("Discount applied:", discount)  # Debug statement
        except Coupons.DoesNotExist:
            coupon = None

    try:
        order = Order.objects.get(user=current_user, is_ordered=False, id=order_id)
    except Order.DoesNotExist:
        return redirect('checkout')

    # Calculate total and other order-related values
    cart_items = CartItem.objects.filter(user=current_user)
    total = sum(cart_item.product.original_price * cart_item.quantity for cart_item in cart_items)
    tax = (2 * total) / 100
    shipping = 100 * sum(cart_item.quantity for cart_item in cart_items)
    grand_total = total + tax + shipping

    # Update order total with discounted total
    order.order_total = grand_total - discount
    order.save()  # Save the updated order

    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'shipping': shipping,
        'tax': tax,
        'discount': discount,
        'grand_total': grand_total - discount,  # Subtract discount from grand total
    }
    return render(request, 'order/payments.html', context)








from django.utils.crypto import get_random_string

#def generate_unique_order_number():
    #order_number = f"{get_random_string(8)}{timezone.now().strftime('%Y%m%d%H%M%S')}"
    #return order_number

def generate_unique_order_number():
    order_number = f"{timezone.now().strftime('%Y%m%d%H%M%S')}"
    return order_number    





@login_required
def place_order(request, total=0, quantity=0):
    current_user = request.user
    coupons = Coupons.objects.all()
    

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('product_list')
    
    unavailable_items = cart_items.filter(product__quantity__lt=F('quantity'))
    if unavailable_items.exists():
        messages.warning(request, 'Some products in your cart are not available in sufficient quantity. Please remove them or update quantities.')
        return redirect('cart') 
    
    tax = 0
    shipping = 0
    grand_total = 0
    discount = 0
    
    if 'coupon_code' in request.session:
        coupon_code = request.session['coupon_code']
        try:
            coupon = Coupons.objects.get(coupon_code=coupon_code)
            if coupon.valid_from <= timezone.now() <= coupon.valid_to and total >= coupon.minimum_amount:
                if not coupon.is_used_by_user(current_user):
                    discount = coupon.discount
        except Coupons.DoesNotExist:
            pass  # Handle invalid coupon gracefully

    for cart_item in cart_items:
        total += (cart_item.product.original_price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    shipping = (100 * quantity)
    grand_total = total + tax + shipping - discount
    
    if request.method == 'POST':
        
        try:
            address = Address.objects.get(user=request.user,is_default=True)
        except:
            messages.warning(request, 'No delivery address exixts! Add a address and try again')
            return redirect('checkout')
        
        
        data = Order()
        data.user = current_user
        data.first_name = address.full_name
        #data.last_name = address.last_name
        data.phone = address.phone
        data.email = address.email
        data.address_line_1 = address.address_line_1
        data.address_line_2 = address.address_line_2
        data.city = address.city
        data.zipcode = address.zipcode
        data.order_total = grand_total
        data.shipping = shipping
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        #data.save()

        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")
        #order_number = current_date + str(data.id)
        #order_number = current_date + str(data.id)
        order_number = generate_unique_order_number()
        data.order_number = order_number
        data.save()

    

      

        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'shipping': shipping,
            'discount': discount,
            'grand_total': grand_total,
            'coupons': coupons,
            
        }
        return render(request, 'order/payments.html', context)
    else:
        return redirect('checkout')
    






from django.shortcuts import redirect,render
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist




def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        order_id = request.POST.get('order_id')
        request.session['coupon_code'] = coupon_code

        try:
            coupon = Coupons.objects.get(coupon_code=coupon_code)
            order = Order.objects.get(id=order_id)

            if coupon.valid_from <= timezone.now() <= coupon.valid_to:
                if order.order_total >= coupon.minimum_amount:
                    if coupon.is_used_by_user(request.user):
                        messages.warning(request, 'Coupon has already been used')
                    else:
                        updated_total = order.order_total - float(coupon.discount)
                        order.order_total = updated_total
                        order.save()

                        used_coupons = UserCoupons(user=request.user, coupon=coupon, is_used=True)
                        used_coupons.save()
                        #deletes session
                        del request.session['coupon_code']

                        return redirect('payments', order_id=order_id)
                else:
                    messages.warning(request, 'Coupon is not applicable for order total')
            else:
                messages.warning(request, 'Coupon is not applicable for the current date')
        except ObjectDoesNotExist:
            messages.warning(request, 'Coupon code is invalid')
        return redirect('payments', order_id=order_id)

    # Redirect to the checkout page if the request method is not POST
    return redirect('payments', order_id=order_id)













def mycoupons(request):
    if request.user.is_authenticated:
        coupons = Coupons.objects.all()
        user = request.user

        coupon_statuses = []

        for coupon in coupons:
            is_used = UserCoupons.objects.filter(coupon=coupon, user=user, is_used=True).exists()
            coupon_statuses.append("Used" if is_used else "Active")

        coupon_data = zip(coupons, coupon_statuses)

        context = {'coupon_data': coupon_data}
        return render(request, 'order/mycoupons.html', context)
    else:
        return redirect('login')

def order_confirmed(request, order_number):
    user = request.user
    order = Order.objects.get(order_number=order_number)

    context = {
        'order': order,
    }
    
    return render(request, 'order/order_confirmed.html',context)



#@transaction.atomic
def confirm_razorpay_payment(request, order_number):
    current_user = request.user
    try:
        order = Order.objects.get(order_number=order_number, user=current_user, is_ordered=False)
    except Order.DoesNotExist:
        return redirect('order_confirmed')
    
    total_amount = order.order_total 

    payment = Payment(
        user=current_user,
        payment_method="Razorpay",
        status="Paid",
        amount_paid=total_amount,
    )
    payment.save()

    order.is_ordered = True
    order.order_number = order_number
    order.payment = payment
    order.save()



    cart_items = CartItem.objects.filter(user=current_user)
    for cart_item in cart_items:
        product=cart_item.product
        stock=product.quantity-cart_item.quantity
        product.quantity=stock
        product.save()
        order_product = OrderProduct(
            order=order,
            payment=payment,
            user=current_user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.product.original_price,
            ordered=True,
        )
        order_product.save()

    cart_items.delete()

    context = {'order': order}

    return render(request, 'order/order_confirmed.html', context)


def wallet_pays(request, order_id):
    user = request.user
    print("Order ID:", order_id)

    # Check if the order exists in the database
    order = get_object_or_404(Order, order_number=order_id)
    #order = Order.objects.get(id = order_id)
    try:
        wallet = Wallet.objects.get(user = user)
        
    except:
        wallet = Wallet.objects.create(user = user, amount=0)
        wallet.save()
        
    if wallet.balance>order.order_total:
        payment = Payment.objects.create(user=user, payment_method='Wallet', amount_paid = order.order_total, status='Paid')
        payment.save()
        order.is_ordered = True
        
        order.payment = payment
        order.save()
        order_total_decimal = Decimal(str(order.order_total))
        wallet.balance -= order_total_decimal
        wallet.save()

        cart_items = CartItem.objects.filter(user=user)
    
        for cart_item in cart_items:
            product=cart_item.product
            stock=product.quantity-cart_item.quantity
            product.quantity=stock
            product.save()
            order_product = OrderProduct(
                order=order,
                payment=payment,
                user=user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                product_price=cart_item.product.original_price,
                ordered=True,
            )
            order_product.save()
        
        cart_items.delete()
        
    else:
        messages.warning(request, 'Not Enough Balance in Wallet')
        return redirect('payments',order_id=order_id)
    context = {
        'order': order,
        'order_number': order.order_number,
        }
    return render(request, 'order/order_confirmed.html', context)


from django.shortcuts import redirect

def wallet_pay(request, order_id):
    user = request.user
    print("Order ID:", order_id)

    # Check if the order exists in the database
    order = get_object_or_404(Order, order_number=order_id)
    
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=user, amount=0)

    if wallet.balance >= order.order_total:
        payment = Payment.objects.create(user=user, payment_method='Wallet', amount_paid=order.order_total, status='Paid')
        payment.save()
        order.is_ordered = True
        order.payment = payment
        order.save()
        
        order_total_decimal = Decimal(str(order.order_total))
        wallet.balance -= order_total_decimal
        wallet.save()

        cart_items = CartItem.objects.filter(user=user)
        for cart_item in cart_items:
            product = cart_item.product
            stock = product.quantity - cart_item.quantity
            product.quantity = stock
            product.save()
            order_product = OrderProduct(
                order=order,
                payment=payment,
                user=user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                product_price=cart_item.product.original_price,
                ordered=True,
            )
            order_product.save()
        
        cart_items.delete()
        
        context = {
            'order': order,
            'order_number': order.order_number,
        }
        return render(request, 'order/order_confirmed.html', context)
    else:
        messages.warning(request, 'Not Enough Balance in Wallet')
        return redirect('payments', order_id=order.id)

