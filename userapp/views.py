from django.shortcuts import render,redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
import threading
from .utils import TokenGenerator,generate_token
from django.views.generic import View
import re
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Category,Product,ProductImage,Address,Wallet
from django.core.paginator import Paginator
from cartapp.models import Cart, CartItem, Coupons, Wishlist, UserCoupons
#from cartapp.views import _cart_id
#import requests
from orderapp.models import Order, OrderProduct, Payment, Address
from decimal import Decimal

# Create your views here.




    

def home(request):
    response = HttpResponse()
    
    products = Product.objects.filter(is_available=True)
    
    # Your view logic here
    context = {
        'request': request, 
        'products': products
         # Pass the request object to the template context
        # Other context data if needed
    }
    return render(request, 'home.html', context)


def handlelogin(request):
    if request.method=="POST":
        username=request.POST['email']
        userpassword=request.POST['pass1']
        myuser=authenticate(username=username,password=userpassword)

        if myuser and not myuser.is_superuser:
            login(request,myuser)
            #messages.success(request,'Login Success')
            return redirect('/')

        else: 
            messages.error(request,"Sign in failed")
            return redirect('/login/')

    return render(request,'user/login.html') 



class EmailThread(threading.Thread):

    def __init__(self,email_message):
      self.email_message=email_message
      threading.Thread.__init__(self)
    def run(self):
      self.email_message.send()




    

def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        try:
            validate_email(email)
        except ValidationError:
            messages.warning(request, "Invalid email address")
            return redirect('/signup/')

        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return redirect('/signup/')
          # Validate phone number format
        if not re.match(r'^\d{10}$', mobile):
            messages.warning(request, "Invalid phone number format. Please enter a 10-digit number.")
            return redirect('/signup/')

        # Validate password strength
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d).{8,}$', password):
            messages.warning(request, "Password should be a minimum of 8 characters and include both letters and numbers.")
            return redirect('/signup/')
       # if User.objects.filter(name=name).exists():
            #messages.warning(request, "Username is already taken")
            #return redirect('/signup')
        try:
            if User.objects.get(username=email):
                messages.info(request,"Email is Taken")
                return render(request,'user/signup.html')
        except Exception as identifier:
            pass
        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email is already taken")
            return redirect('/signup/')
        
        
        
        user = User.objects.create_user(username=email,email=email,first_name=name,password=password,last_name=mobile)
    
        user.is_active=False
        user.save()

        current_site = get_current_site(request)
        email_subject = "Please acivate your Account"
        message = render_to_string('user/signup_verification.html',{
            'user': user,
            'domain': '127.0.0.1:8000',
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user),
        })
        email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
        EmailThread(email_message).start()
        email_message.send()
        messages.info(request, "Please click on the link send to your email to Activate your Account")
        return redirect('/login/')

       

    return render(request, 'user/signup.html')

class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            #uid=force_text(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Successfully")
            return redirect('/login/')
        else:
            messages.warning(request,"Invalid activation link")    
            return redirect('/signup/')    


#def handlelogout(request):
   # logout(request)
    #messages.info(request,"Logout Success")
    #return  redirect('/login/')   

def handlelogout(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        logout(request)
    return redirect('/login/') 


def forgot_password(request):

    if request.method == "POST":
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string('user/password_verification.html',{
                'user': user,
                'domain': '127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user),
            })
            to_email = email
            send_email  = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request,"Password reset email has been sent to your email address ")
            return redirect('/login/')

        else:
            messages.warning(request, 'Account does not exist!')
    else:
        return render(request, 'user/forgot_password.html')







class password_validation(View):
    def get(self,request,uidb64,token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            #uid=force_text(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
            #user = User._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, ValidationError ,User.DoesNotExist):
            print(f"Exception during password validation: {e}")
            user=None
         

        if user is not None and generate_token.check_token(user,token):
            request.session['uid'] = uid
            messages.success(request, 'Please Reset your Password!!')
            return redirect('reset_password')
        else:
            messages.warning(request, 'Link has been expired')
            return redirect('/login/')  

def reset_password(request):

    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset Successfull')
            return redirect('/login/')

        else:
            messages.warning(request, 'Passwords do not match')
            return redirect("reset_password")
    else:
        return render(request, 'user/reset_password.html') 





def product_list(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')

    if selected_category_id:
        selected_category = Category.objects.get(id=selected_category_id)
        products = Product.objects.filter(category=selected_category, is_available=True).order_by('created_date')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    else:
        products = Product.objects.filter(is_available=True).order_by('created_date')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    context = {
        'categories': categories,
        'products': paged_products,
    }

    return render(request, 'user/product_list.html', context)





 



def product_detail(request, category_id, product_id, selected_image=None):
    categories = Category.objects.all()

    try:
        selected_category = Category.objects.get(id=category_id)
        single_product = Product.objects.get(category=selected_category, id=product_id, is_available=True)
        product_images = single_product.images.all()
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'is_out_of_stock': single_product.quantity <= 0,
        'product_images': product_images,   
    }
    return render(request, 'user/product_detail.html', context)      


@login_required
def user_profile(request):
    return render(request, 'user/user_profile.html')




@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        new_name = request.POST.get('name')
        new_mobile = request.POST.get('mobile')
        new_email = request.POST.get('email')

        if User.objects.filter(username=new_email).exclude(id=user.id).exists():
            messages.warning(request, 'Username is already taken')
            return redirect('edit_profile')

        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.warning(request, 'Email is already taken')
            return redirect('edit_profile')

        if User.objects.filter(last_name=new_mobile).exclude(id=user.id).exists():
            messages.warning(request, 'Mobile number is already taken')
            return redirect('edit_profile')

        
        user.username = new_email
        user.first_name=new_name
        user.last_name = new_mobile
        user.email = new_email
        user.save()

        messages.success(request, 'Profile updated successfully')
        return redirect('user_profile')

    return render(request, 'user/user_profile.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = User.objects.get(username__exact=request.user.username)
    
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, 'Password Changed Successfully')
                return redirect('/login/')
            else:
                messages.warning(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.warning(request, 'Password does not match')
            return redirect('change_password')

    return render(request, 'user/change_password.html') 

def search(request):
    products = []
    categories = Category.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('product_name').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))

    context = {
        'products': products,
        'categories':categories,
    }
    return render(request, 'user/product_list.html', context)       


def add_address(request):
    if request.method == 'POST':
        full_name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        zipcode = request.POST.get('zipcode')


        address = Address(user=request.user, full_name=full_name, phone=phone, email=email, address_line_1=address_line_1, address_line_2=address_line_2, city=city, zipcode=zipcode)
        address.save()


        if request.user.is_authenticated:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.is_default = True
            address.save()

        source = request.GET.get('source', 'checkout')
        messages.success(request, 'New address added successfully.')
        #redirect to checkout to be added
        if source == 'checkout':
            return redirect('checkout')
        else:
            return redirect('add_address')
    else:
        return render(request, 'user/add_address.html')


@login_required
def manage_address(request):
    current_user = request.user
    addresses = Address.objects.filter(user=current_user)
    context = {
        'addresses': addresses,
    }
    return render(request, 'user/manage_address.html', context)


@login_required
def edit_address(request, address_id):
    address = Address.objects.get(pk=address_id)

    if request.method == 'POST':

        address.full_name = request.POST.get('name')
        address.email = request.POST.get('email')
        address.phone = request.POST.get('phone')
        address.address_line_1 = request.POST.get('address_line_1')
        address.address_line_2 = request.POST.get('address_line_2')
        address.city = request.POST.get('city')
        address.pincode = request.POST.get('pincode')

        address.save()

        messages.success(request, 'Address updated successfully.')

        return redirect('edit_address', address_id=address.id)

    

    context = {
        'address': address,
    }
    return render(request, 'user/edit_address.html', context)



def delete_address(request, address_id):

    address = Address.objects.get(pk=address_id)
    address.delete()

    return redirect('manage_address')


def order_history(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, 'user/dashboard.html', context)


#def view_order(request, order_id):
    #order_products = OrderProduct.objects.filter(order__user=request.user, order__id=order_id)
    #orders = Order.objects.filter(is_ordered=True, id=order_id)
    
    #payments = Payment.objects.filter(order__id=order_id)

    #for order_product in order_products:
        #order_product.total = order_product.quantity * order_product.product_price

    #context = {
        #'order_products': order_products,
        #'orders': orders,
       # 'payments': payments,
    #}

    #return render(request, 'user/view_order.html', context)


def view_order(request,order_id):
    payment_pending_msg = None
    user = request.user
    try:
       
        
        order = Order.objects.get(id=order_id)
        order_products = OrderProduct.objects.filter(order=order)
        coupon_code = request.session.get('coupon_code', None) 
        coupon = None 

        if coupon_code:
            try:
                coupon = Coupons.objects.get(coupon_code=coupon_code)
            except Coupons.DoesNotExist:
                coupon = None
        try:
             payment = Payment.objects.get(order=order)
        except Payment.DoesNotExist:
             payment = None
             payment_pending_msg = "Payment pending"
        #payment = Payment.objects.get(order=order)
        cart_items = CartItem.objects.filter(user=user)

        total = 0
        tax = 0
        shipping = 0
        grand_total = 0  

        subtotal = 0  
        order_item_total=[]
        for order_item in order_products:
            order_item_total = order_item.product.original_price * order_item.quantity
            order_item.total = order_item_total  
            subtotal += order_item_total
            shipping += 100*(order_item.quantity)

        tax = (2 * subtotal) / 100
        

        grand_total = subtotal + tax + shipping - (coupon.discount if coupon else 0) 
        if not payment:
            payment_pending_msg = "Payment pending" 

        context = {
            'order': order,
            'order_products': order_products,
            'payment': payment,
            'payment_pending_msg' : payment_pending_msg,
            'grand_total': grand_total,
            'cart_items': cart_items,
            'order_item_total': order_item_total,
            'total': total,
            'shipping':shipping,
            'discount': coupon.discount if coupon else 0,  
            'subtotal': subtotal,
            'coupon_code':coupon_code,
        }
        if coupon_code:  # Only include coupon code in context if it's applied
            context['coupon_code'] = coupon_code
    except Order.DoesNotExist:
        messages.error(request, 'Order does not exist.')  
        return redirect('product_list')      

     
    return render(request, 'user/vieworderdetail.html', context)




def view_orders(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_products = OrderProduct.objects.filter(order=order)
   

    context = {
        'order': order,
        'order_products': order_products,
   }

    return render(request,'user/view_order.html', context)


def cancel_order_product(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'Cancelled':
        order.status = 'Cancelled'
        canceled_amount = Decimal(str(order.order_total))
        order.save()

        # Increase view_count for each OrderProduct
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            product = order_product.product
            product.quantity += order_product.quantity
            product.save()

        user = request.user
        user_wallet, created = Wallet.objects.get_or_create(user=user)
        user_wallet.balance += canceled_amount
        user_wallet.save()

    return redirect('view_order', order_id=order.id)    


def invoice_view(request, order_id):
    user = request.user
    try:
        order = Order.objects.get(id=order_id)
        order_items = OrderProduct.objects.filter(order=order)
        coupon_code = request.session.get('coupon_code', None) 
        coupon = None 

        if coupon_code:
            try:
                coupon = Coupons.objects.get(coupon_code=coupon_code)
            except Coupons.DoesNotExist:
                coupon = None

        payment = Payment.objects.get(order=order)
        cart_items = CartItem.objects.filter(user=user)

        total = 0
        tax = 0
        shipping = 0
        grand_total = 0  

        subtotal = 0 
        order_item_totals = [] 
        for order_item in order_items:
            order_item_total = order_item.product.original_price * order_item.quantity
            order_item.total = order_item_total  
            subtotal += order_item_total
            
            #shipping = 100 * sum(order_item.quantity for order_item in cart_items)
            shipping += 100*(order_item.quantity)

        tax = (2 * subtotal) / 100
        
        #shipping = 100 * sum(cart_item.quantity for cart_item in cart_items)
        print(shipping)
        grand_total = subtotal + tax + shipping - (coupon.discount if coupon else 0)  

        context = {
            'order': order,
            'order_items': order_items,
            'payment': payment,
            'grand_total': grand_total,
            'cart_items': cart_items,
            'order_item_totals': order_item_totals,
            'total': total,
            'shipping':shipping,
            'discount': coupon.discount if coupon else 0,  
            'subtotal': subtotal,
        }

    except Order.DoesNotExist:
        messages.error(request, 'Order does not exist.')  
        return redirect('product_list')  
    return render(request, 'user/invoice.html', context)


#def invoice_view(request, order_id):
    #order = get_object_or_404(Order, id=order_id)
    #order_products = OrderProduct.objects.filter(order=order)
    
    #context = {
        #'order': order,
        #'order_products': order_products,
    #}
    
    #return render(request, 'user/invoice.html', context)

def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_products = OrderProduct.objects.filter(order=order)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Invoice - Order ID: {order.id}", styles['Heading1']))
    elements.append(Paragraph(f"Order Date: {order.created_at}", styles['Normal']))
    elements.append(Paragraph(f"Total Amount: {order.order_total}", styles['Normal']))
    elements.append(Paragraph(f"Status: {order.status}", styles['Normal']))
    
    # Display user details
    user = order.user
    elements.append(Paragraph(f"User: {user.username}", styles['Normal']))
    elements.append(Paragraph(f"Email: {user.email}", styles['Normal']))
    elements.append(Paragraph(f"First Name: {user.first_name}", styles['Normal']))
    elements.append(Paragraph(f"Last Name: {user.last_name}", styles['Normal']))
    
    data = [['Product', 'Quantity', 'Price', 'Variation']]
    for item in order_products:
        data.append([item.product.title, item.quantity, item.product_price, item.variation])
    
    table = Table(data, colWidths=[200, 50, 75, 150])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    elements.append(table)
    doc.build(elements)

    return response        



#@login_required(login_url='user_login')
def my_wallet(request):
    current_user = request.user
    try:
        wallet = Wallet.objects.get(user=current_user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=current_user, balance=0)
    wallet_amount = wallet.balance
  
    context = {'wallet_amount': wallet_amount}

    return render(request, 'user/wallet.html', context)


#@login_required(login_url='user_login')
def wallet_pay(request, order_number):
    user = request.user
    print("Order ID:", order_number)

    # Check if the order exists in the database
    order = get_object_or_404(Order, order_number=order_number)
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
        wallet.amount -= order.order_total
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
                product_price=cart_item.product.price,
                ordered=True,
            )
            order_product.save()
        
        cart_items.delete()
        
    else:
        messages.warning(request, 'Not Enough Balance in Wallet')
        return redirect('orderapp:payments')
    context = {
        'order': order,
        'order_number': order.order_number,
        }
    return render(request, 'order/order_confirmed.html', context)


    
from django.http import JsonResponse
from .models import Product

from django.http import JsonResponse

def handle_price_range(request):
    if request.method == 'GET':
        # Retrieve the minimum and maximum price values from the request
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        # Ensure min_price and max_price are numeric
        try:
            min_price = float(min_price)
            max_price = float(max_price)
        except (TypeError, ValueError):
            # Handle case where min_price or max_price is not provided or not numeric
            return JsonResponse({'success': False, 'message': 'Invalid price range'}, status=400)

        # Filter products based on the received price range
        products = Product.objects.filter(original_price__range=(min_price, max_price))

        # Convert queryset to a list of dictionaries for JSON serialization
        products_data = [{'id': product.id, 'name': product.product_name, 'price': product.original_price} for product in products]

        if not products_data:
            return JsonResponse({'success': False, 'message': 'No products found in the specified price range'})

        # For demonstration purposes, let's return the filtered products data
        response_data = {
            'success': True,
            'message': 'Products filtered successfully',
            'products': products_data,
        }

        # Return a JSON response with the filtered products data
        return JsonResponse(response_data)
    else:
        # Handle invalid request method (e.g., POST, PUT, DELETE)
        response_data = {
            'success': False,
            'message': 'Invalid request method'
        }
        return JsonResponse(response_data, status=405)  # Method Not Allowed





def handle_price_rangess(request):
    if request.method == 'GET':
        # Retrieve the minimum and maximum price values from the request
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        # Filter products based on the received price range
        products = Product.objects.filter(original_price__range=(min_price, max_price))

        # Convert queryset to a list of dictionaries for JSON serialization
        products_data = [{'id': product.id, 'name': product.product_name, 'price': product.original_price} for product in products]

        # For demonstration purposes, let's return the filtered products data
        response_data = {
            'success': True,
            'message': 'Products filtered successfully',
            'products': products_data,
        }

        # Return a JSON response with the filtered products data
        return JsonResponse(response_data)
    else:
        # Handle invalid request method (e.g., POST, PUT, DELETE)
        response_data = {
            'success': False,
            'message': 'Invalid request method'
        }
        return JsonResponse(response_data, status=405)  # Method Not Allowed
        


        from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import DecimalField

def handle_price_rangessss(request):
    if request.method == 'GET':
        # Retrieve the minimum and maximum price values from the request
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        # Convert the price values to DecimalField for proper comparison
        try:
            min_price = DecimalField().to_python(min_price)
            max_price = DecimalField().to_python(max_price)
        except ValidationError:
            # Handle invalid price values
            return JsonResponse({'success': False, 'message': 'Invalid price values'}, status=400)

        # Filter products based on the received price range
        products = Product.objects.all()
        if min_price is not None:
            products = products.filter(original_price__gte=min_price)
        if max_price is not None:
            products = products.filter(original_price__lte=max_price)

        # Convert queryset to a list of dictionaries for JSON serialization
        products_data = [{'id': product.id, 'name': product.product_name, 'price': product.original_price} for product in products]

        # For demonstration purposes, let's return the filtered products data
        response_data = {
            'success': True,
            'message': 'Products filtered successfully',
            'products': products_data,
        }

        # Return a JSON response with the filtered products data
        return JsonResponse(response_data)
    else:
        # Handle invalid request method (e.g., POST, PUT, DELETE)
        response_data = {
            'success': False,
            'message': 'Invalid request method'
        }
        return JsonResponse(response_data, status=405)  # Method Not Allowed


from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import DecimalField
from .models import Product

def handle_price_ranges(request):
    if request.method == 'GET':
        # Retrieve the minimum and maximum price values from the request
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        # Validate and convert the price values to DecimalField for proper comparison
        try:
            if min_price is not None:
                min_price = DecimalField().clean(min_price)
            if max_price is not None:
                max_price = DecimalField().clean(max_price)
        except ValidationError:
            # Handle invalid price values
            return JsonResponse({'success': False, 'message': 'Invalid price values'}, status=400)

        # Filter products based on the received price range
        products = Product.objects.all()
        if min_price is not None:
            products = products.filter(original_price__gte=min_price)
        if max_price is not None:
            products = products.filter(original_price__lte=max_price)

        # Convert queryset to a list of dictionaries with product details
        products_data = [
            {
                'id': product.id,
                'name': product.product_name,
                'price': product.original_price,
                'image_url': product.get_image_url(),  # Replace this with the actual method to get the product image URL
                'url': product.get_absolute_url(),  # Replace this with the actual method to get the product detail URL
                'add_to_cart_url': product.get_add_to_cart_url(),  # Replace this with the actual method to get the add to cart URL
            }
            for product in products
        ]

        # Prepare the response data
        response_data = {
            'success': True,
            'message': 'Products filtered successfully',
            'products': products_data,
        }

        # Return a JSON response with the filtered products data
        return JsonResponse(response_data)
    else:
        # Handle invalid request method (e.g., POST, PUT, DELETE)
        response_data = {
            'success': False,
            'message': 'Invalid request method'
        }
        return JsonResponse(response_data, status=405)  # Method Not Allowed




def sort_lists(request):
    # Fetch all products from the database
    products = Product.objects.all()
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Sorting products based on query parameters

    sort_by = request.GET.get('sort_by')
    if sort_by == 'price':
        products = products.order_by('original_price')
    elif sort_by == 'name':
        products = products.order_by('product_name')
    elif sort_by == '-price':
        products = products.order_by('-original_price')
    elif sort_by == '-name':
        products = products.order_by('-product_name')      

    context = {
        'products': products,
        'categories':categories,
    }
    return render(request, 'user/product_list.html', context)


def sort_list(request):
    # Fetch all products from the database
    products = Product.objects.all()
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    
    # Filter products by category if category_id is provided
    if category_id:
        products = products.filter(category_id=category_id)

    # Sorting products based on query parameters
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price':
        products = products.order_by('original_price')
    elif sort_by == '-price':
        products = products.order_by('-original_price')
    elif sort_by == 'name':
        products = products.order_by('product_name')
    elif sort_by == '-name':
        products = products.order_by('-product_name')

    context = {
        'products': products,
        'categories': categories,
        'category_id': category_id,
    }
    return render(request, 'user/product_list.html', context)
