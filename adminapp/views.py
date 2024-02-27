from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User, auth
from userapp.models import Category,Product,ProductImage
from django.contrib.auth.decorators import login_required
from orderapp.models import Order,OrderProduct,Payment
from cartapp.models import Coupons,UserCoupons
from datetime import datetime, timedelta
from django.db.models import Count,Sum
from decimal import Decimal
from django.shortcuts import get_object_or_404
# Create your views here.




def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
        
            if user is not None and user.is_active and user.is_superuser:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials")
        else:
            messages.error(request, "Please provide both username and password")
        
        return redirect('index')
         
    return render(request, 'adminapp/index.html')


#def dashboard(request):
    #return render(request,'adminapp/indexevara.html')


@login_required
def dashboard(request):
    if request.user.is_superuser:
        if not request.user.is_superuser:
            return redirect('index')
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        recent_orders = Order.objects.filter(is_ordered=True).order_by('-created_at')[:10]

        last_year = end_date - timedelta(days=365)
        yearly_order_counts = (
            Order.objects
            .filter(created_at__range=(last_year, end_date), is_ordered=True)
            .values('created_at__year')
            .annotate(order_count=Count('id'))
            .order_by('created_at__year')
        )

        month = end_date - timedelta(days=30)
        monthly_earnings = (
            Order.objects
            .filter(created_at__range=(month, end_date), is_ordered=True)
            .aggregate(total_order_total=Sum('order_total'))
        )['total_order_total'] or Decimal('0.00')

        monthly_earnings = Decimal(monthly_earnings).quantize(Decimal('0.00'))

        daily_order_counts = (
            Order.objects
            .filter(created_at__range=(start_date, end_date), is_ordered=True)
            .values('created_at__date')
            .annotate(order_count=Count('id'))
            .order_by('created_at__date')
        )

        dates = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in daily_order_counts]
        counts = [entry['order_count'] for entry in daily_order_counts]

        context = {
            'admin_name': request.user.first_name,
            'dates': dates,
            'counts': counts,
            'orders': recent_orders,
            'yearly_order_counts': yearly_order_counts,
            'monthly_earnings': monthly_earnings,
            'order_count': len(recent_orders),
        }

        return render(request, 'adminapp/dashboard.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")


from django.utils import timezone
from django.db.models.functions import ExtractMonth,ExtractWeek
from django.db.models.functions import ExtractMonth

from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal




@login_required
def dashboards(request):
    if request.user.is_superuser:
        # Redirect non-superusers to index page
        if not request.user.is_superuser:
            return redirect('index')
        end_date = datetime.now()
        current_date = timezone.now().date()
        start_of_month = current_date.replace(day=1)
        end_of_month = start_of_month.replace(month=start_of_month.month + 1) - timedelta(days=1)
        start_of_today = current_date
        end_of_today = start_of_today + timedelta(days=1)
        start_of_last_month = current_date - timedelta(days=30)
        last_year = current_date - timedelta(days=365)  # Calculate last year

        orders1 = Order.objects.filter(created_at__range=[start_of_last_month, start_of_last_month + timedelta(days=6)]).order_by('-created_at')
        amount1 = orders1.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0
        
        orders2 = Order.objects.filter(created_at__range=[start_of_last_month + timedelta(days=7), start_of_last_month + timedelta(days=14)]).order_by('-created_at')
        amount2 = orders2.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0
        
        orders3 = Order.objects.filter(created_at__range=[start_of_last_month + timedelta(days=15), start_of_last_month + timedelta(days=20)]).order_by('-created_at')
        amount3 = orders3.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0
        
        orders4 = Order.objects.filter(created_at__range=[start_of_last_month + timedelta(days=21), end_of_today]).order_by('-created_at')
        amount4 = orders4.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0

        six_days_before = current_date - timedelta(days=6)
        morning_start6 = datetime.combine(six_days_before , datetime.min.time())
        evening_end6 = datetime.combine(six_days_before , datetime.max.time())
        ordersd1 = Order.objects.filter(created_at__range=[morning_start6, evening_end6]).order_by('-created_at')
        amountd1 = ordersd1.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0

        five_days_before = current_date - timedelta(days=5)
        morning_start5 = datetime.combine(five_days_before, datetime.min.time())
        evening_end5 = datetime.combine(five_days_before, datetime.max.time())
        ordersd2 = Order.objects.filter(created_at__range=[morning_start5, evening_end5]).order_by('-created_at')
        amountd2 = ordersd2.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0

        four_days_before = current_date - timedelta(days=4)
        morning_start4 = datetime.combine(four_days_before, datetime.min.time())
        evening_end4 = datetime.combine(four_days_before, datetime.max.time())
        ordersd3 = Order.objects.filter(created_at__range=[morning_start4, evening_end4]).order_by('-created_at')
        amountd3 = ordersd3.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0

        three_days_before = current_date - timedelta(days=3)
        morning_start3 = datetime.combine(three_days_before, datetime.min.time())
        evening_end3 = datetime.combine(three_days_before, datetime.max.time())
        ordersd4 = Order.objects.filter(created_at__range=[morning_start3, evening_end3]).order_by('-created_at')
        amountd4 = ordersd4.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0

        two_days_before = current_date - timedelta(days=2)
        morning_start2 = datetime.combine(two_days_before, datetime.min.time())
        evening_end2 = datetime.combine(two_days_before, datetime.max.time())
        ordersd5 = Order.objects.filter(created_at__range=[morning_start2, evening_end2]).order_by('-created_at')
        amountd5 = ordersd5.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0

        one_day_before = current_date - timedelta(days=1)
        morning_start1 = datetime.combine(one_day_before, datetime.min.time())
        evening_end1 = datetime.combine(one_day_before, datetime.max.time())
        ordersd6 = Order.objects.filter(created_at__range=[morning_start1, evening_end1]).order_by('-created_at')
        amountd6 = ordersd6.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0


        zero_day_before = current_date - timedelta(days=0)
        morning_start0 = datetime.combine(zero_day_before, datetime.min.time())
        evening_end0 = datetime.combine(zero_day_before, datetime.max.time())
        ordersd7 = Order.objects.filter(created_at__range=[morning_start0, evening_end0]).order_by('-created_at')
        amountd7 = ordersd7.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0
   





        first_day_current_month = current_date.replace(day=1)
        evening_end = datetime.combine(current_date, datetime.max.time())
        ordersdfeb = Order.objects.filter(created_at__range=[first_day_current_month, evening_end]).order_by('-created_at')
        amountfeb = ordersdfeb.aggregate(total_order_amount=Sum('order_total'))['total_order_amount'] or 0

        recent_orders = Order.objects.filter(is_ordered=True).order_by('-created_at')[:10]

        month = end_date - timedelta(days=30)
        monthly_earnings = (
            Order.objects
            .filter(created_at__range=(month, end_date), is_ordered=True)
            .aggregate(total_order_total=Sum('order_total'))
        )['total_order_total'] or Decimal('0.00')

        monthly_earnings = Decimal(monthly_earnings).quantize(Decimal('0.00'))
        start_of_current_month = current_date.replace(day=1)
        end_of_current_month = start_of_current_month.replace(month=start_of_current_month.month + 1) - timedelta(days=1)
        
        # Fetch weekly order amounts for the current month
        weekly_order_counts = (
            Order.objects
            .filter(created_at__range=(start_of_current_month, end_of_current_month), is_ordered=True)
            .annotate(week=ExtractWeek('created_at'))
            .values('week')
            .annotate(order_amount=Sum('order_total'))
            .order_by('week')
        )

        
        last_year = end_date - timedelta(days=365)
        yearly_order_counts = (
            Order.objects
            .filter(created_at__range=(last_year, end_date), is_ordered=True)
            .values('created_at__year')
            .annotate(order_count=Count('id'))
            .order_by('created_at__year')
        )
        #yearly_order_counts = (
           # Order.objects
            #.filter(created_at__range=(last_year, current_date), is_ordered=True)
            #.values('created_at__year')
            #.annotate(order_count=Count('id'))
            #.order_by('created_at__year')
       # )

        monthly_order_counts = (
            Order.objects
            .filter(created_at__range=(start_of_last_month, current_date), is_ordered=True)
            .values('created_at__month')
            .annotate(order_count=Count('id'))
            .order_by('created_at__month')
        )

       

        #month = current_date - timedelta(days=30)
        #monthly_earnings = (
            #Order.objects
            #.filter(created_at__range=(month, current_date), is_ordered=True)
            #.aggregate(total_order_total=Sum('order_total'))
        #)['total_order_total'] or Decimal('0.00')

        #monthly_earnings = Decimal(monthly_earnings).quantize(Decimal('0.00'))

        daily_order_counts = (
            Order.objects
            .filter(created_at__range=(start_of_today, end_of_today), is_ordered=True)
            .values('created_at__date')
            .annotate(order_count=Count('id'))
            .order_by('created_at__date')
        )

        dates = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in daily_order_counts]
        counts = [entry['order_count'] for entry in daily_order_counts]
        recent_orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
        context = {
            'admin_name': request.user.first_name,
            'dates': dates,
            'counts': counts,
            'orders': recent_orders,
            'yearly_order_counts': yearly_order_counts,
            'monthly_order_counts': monthly_order_counts,
            'weekly_order_counts': weekly_order_counts,
            'monthly_earnings': monthly_earnings,
            'order_count': len(recent_orders),
            'amount1': amount1,
            'amount2': amount2,
            'amount3': amount3,
            'amount4': amount4,
            'amountd1': amountd1,
            'amountd2': amountd2,
            'amountd3': amountd3,
            'amountd4': amountd4,
            'amountd5': amountd5,
            'amountd6': amountd6,
            'amountd7': amountd7,

            'amountfeb': amountfeb,
        }

        return render(request, 'adminapp/dashboardnew.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")

   

def dashboard_admin(request):
    products=Product.objects.all()
    products_with_order_counts = Product.objects.annotate(order_count=Count('orderproduct'))
    products_with_more_orders = products_with_order_counts.order_by('-order_count')[:10]
    category=Category.objects.all()
    categories_with_most_orders = Category.objects.annotate(num_orders=Count('product__orderproduct')).order_by('-num_orders')[:10]
    #brands_with_most_orders = Brand.objects.annotate(num_orders=Count('product__orderproduct')).order_by('-num_orders')[:10]

    current_date = timezone.now().date()
  # Calculate start and end of the month
    start_of_month = current_date.replace(day=1)
    end_of_month = start_of_month.replace(month=start_of_month.month + 1) - timedelta(days=1)
  # Calculate the start of today
    start_of_today = current_date
    end_of_today = start_of_today + timedelta(days=1)
   # Calculate the start of the month one month ago
    start_of_last_month = current_date - timedelta(days=30)
   
  # Filter Order objects for today and the past month
    orders1 = Order.objects.filter(created_at__range=[start_of_last_month, start_of_last_month + timedelta(days=6)]).order_by('-created_at')
    amount1 = orders1.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0
   
    orders2 = Order.objects.filter(created_at__range=[start_of_last_month + timedelta(days=7), start_of_last_month + timedelta(days=14)]).order_by('-created_at')
    amount2 = orders2.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0
   
    orders3 = Order.objects.filter(created_at__range=[start_of_last_month + timedelta(days=15), start_of_last_month + timedelta(days=20)]).order_by('-created_at')
    amount3 = orders3.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0
    orders4 = Order.objects.filter(created_at__range=[start_of_last_month + timedelta(days=21), end_of_today]).order_by('-created_at')
    amount4 = orders4.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0


    six_days_before = current_date - timedelta(days=6)
    morning_start6 = datetime.combine( six_days_before , datetime.min.time())
    evening_end6 = datetime.combine( six_days_before , datetime.max.time())
    
    

# Filter orders for the last week
    ordersd1 = Order.objects.filter(
    created_at__range=[  morning_start6, evening_end6]
                  ).order_by('-created_at')
    # Calculate the sum of order amount for the current day
    amountd1 = ordersd1.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0
    
    five_days_before = current_date - timedelta(days=5)
    morning_start5 = datetime.combine(five_days_before, datetime.min.time())
    evening_end5 = datetime.combine(five_days_before, datetime.max.time())
    ordersd2 = Order.objects.filter(created_at__range=[ morning_start5, evening_end5]).order_by('-created_at')
    # Calculate the sum of order amount for the current day
    amountd2 = ordersd2.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0
    
   
    four_days_before = current_date - timedelta(days=4)
    morning_start4 = datetime.combine(four_days_before, datetime.min.time())
    evening_end4 = datetime.combine(four_days_before, datetime.max.time())
    ordersd3 = Order.objects.filter(created_at__range=[ morning_start4, evening_end4]).order_by('-created_at')
    # Calculate the sum of order amount for the current day
    amountd3 = ordersd3.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0
    
    
    three_days_before = current_date - timedelta(days=3)
    morning_start3 = datetime.combine(three_days_before, datetime.min.time())
    evening_end3 = datetime.combine(three_days_before, datetime.max.time())
    ordersd4 = Order.objects.filter(created_at__range=[ morning_start3, evening_end3]).order_by('-created_at')
    # Calculate the sum of order amount for the current day
    amountd4 = ordersd4.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0
    
    two_days_before = current_date - timedelta(days=2)
    morning_start2 = datetime.combine(two_days_before, datetime.min.time())
    evening_end2 = datetime.combine(two_days_before, datetime.max.time())
    ordersd5 = Order.objects.filter(created_at__range=[morning_start2, evening_end2]).order_by('-created_at')
    # Calculate the sum of order amount for the current day
    amountd5 = ordersd5.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0
    
    one_day_before = current_date - timedelta(days=1)
    morning_start1 = datetime.combine(one_day_before, datetime.min.time())
    evening_end1 = datetime.combine(one_day_before, datetime.max.time())
    ordersd6 = Order.objects.filter(created_at__range=[morning_start1, evening_end1]).order_by('-created_at')
    # Calculate the sum of order amount for the current day
    amountd6 = ordersd6.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0


    morning_start = datetime.combine(current_date, datetime.min.time())
    evening_end = datetime.combine(current_date, datetime.max.time())
    ordersd7 = Order.objects.filter(created_at__range=[morning_start, evening_end]).order_by('-created_at')
    # Calculate the sum of order amount for the current day
    amountd7 = ordersd7.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0

    first_day_current_month = current_date.replace(day=1)
    evening_end = datetime.combine(current_date, datetime.max.time())
    
   
    ordersdfeb = Order.objects.filter(created_at__range=[first_day_current_month,evening_end]).order_by('-created_at')
    
    # Calculate the sum of order amount for the current day
    amountfeb = ordersdfeb.aggregate(total_order_amount=Sum('order_total'))[
                             'total_order_amount'] or 0
    

    return render(request,'adminapp/dashboard_admin.html',{'products':products,'products_with_more_orders':products_with_more_orders,'categories_with_most_orders':categories_with_most_orders,'amount1':amount1,'amount2':amount2,'amount3':amount3,'amount4':amount4,'amountd1':amountd1,'amountd2':amountd2,'amountd3':amountd3,'amountd4':amountd4,'amountd5':amountd5,'amountd6':amountd6,'amountd7':amountd7,'amountfeb':amountfeb})








def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')

def admin_users(request):
    users = User.objects.filter(is_superuser=False).order_by('id')  
    context = {'users': users}
    return render(request, 'adminapp/admin_users.html', context)

def block_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('admin_users')
    user.is_active = False
    user.save()
    return redirect('admin_users')  


def unblock_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('admin_users')
    user.is_active = True
    user.save()
    return redirect('admin_users')

#def admin_category(request):
   # return render(request,'adminapp/admin_category.html')




def admin_category(request):
    categories = Category.objects.all().order_by('id')  
    context = {'categories': categories}
    return render(request, 'adminapp/admin_category.html', context)


def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_image = request.FILES.get('category_image')

        if not category_name:
            messages.error(request, "Please provide a category name.")
            return redirect('add_category')

        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, f"A category with the name '{category_name}' already exists.")
            return redirect('add_category')

        category = Category(
            category_name=category_name,
            category_images=category_image
        )
        category.save()

        return redirect('admin_category')

    return render(request, 'adminapp/add_category.html')

def edit_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_image = request.FILES.get('category_image')

        if not category_name:
            messages.error(request, "Please provide a category name.")
            return redirect('edit_category', category_id=category_id)

        if Category.objects.filter(category_name=category_name).exclude(pk=category_id).exists():
            messages.error(request, f"A category with the name '{category_name}' already exists.")
            return redirect('edit_category', category_id=category_id)

        category.category_name = category_name
        if category_image:
            category.category_images = category_image
        category.save()

        return redirect('admin_category')

    context = {'category': category}
    return render(request, 'adminapp/edit_category.html', context)




def soft_delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')
    category.soft_deleted = True
    category.is_available = False
    category.save()
    return redirect('admin_category')


def undo_soft_delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('admin_category')
    category.soft_deleted = False
    category.is_available = True
    category.save()
    return redirect('admin_category')

#Product management
@login_required
def admin_products(request):
    
    if request.user.is_superuser:
        # Exclude soft-deleted products
        products = Product.objects.select_related('category').order_by('id')

        # Add a status field to indicate availability
        for product in products:
            product.status = "Available" if product.is_available else "Unavailable"

        context = {'products': products}
        return render(request, 'adminapp/admin_products.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")
    




def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_images = request.FILES.getlist('product_images') 
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')

        # Store the form data in a dictionary to pass it back to the form in case of errors
        form_data = {
            'product_name': product_name,
            'category_id': category_id,
            'description': description,
            'price': price,
            'quantity': quantity,
        }

        if not (product_name and category_id and price and quantity):
            messages.error(request, "Please provide all required fields.")
            return render(request, 'adminapp/add_product.html', {'categories': Category.objects.all().order_by('id'), 'form_data': form_data})
       
        try:
            price = float(price)
            quantity = int(quantity)
            if price <= 0 or quantity <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Price and quantity must be positive numbers.")
            return render(request, 'adminapp/add_product.html', {'categories': Category.objects.all().order_by('id'), 'form_data': form_data})
        
        if Product.objects.filter(product_name=product_name).exists():
            messages.error(request, f"A product with the name '{product_name}' already exists.")
            return render(request, 'adminapp/add_product.html', {'categories': Category.objects.all().order_by('id'), 'form_data': form_data})
        
        # If there are any error messages, render the form with error messages and form data
        if messages.get_messages(request):
            return render(request, 'adminapp/add_product.html', {'categories': Category.objects.all().order_by('id'), 'form_data': form_data})

        try:
            category = Category.objects.get(pk=category_id)
            if product_images:
                first_image = product_images[0]
                product = Product(
                    product_name=product_name,
                    category=category,
                    description=description,
                    original_price=price,
                    selling_price=price,
                    product_images=first_image,
                    quantity=quantity,
                    is_available=True
                )
                product.save()
                
                for image in product_images:
                    ProductImage.objects.create(product=product, image=image)
                
                return redirect('admin_products')
            else:
                messages.error(request, "Please upload at least one product image.")
        except Exception as e:
            messages.error(request, str(e))
    
    # If it's a GET request or if there are errors, render the form with the categories
    return render(request, 'adminapp/add_product.html', {'categories': Category.objects.all().order_by('id')})




@login_required
def edit_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return redirect('admin_products')

    categories = Category.objects.all().order_by('id')

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')

        # Validate form data
        if not (product.product_name and category_id and price and quantity):
            messages.error(request, "Please provide all required fields.")
            # Pass the submitted data to the template
            context = {'product': product, 'categories': categories}
            return render(request, 'adminapp/edit_product.html', context)

        try:
            price = float(price)
            quantity = int(quantity)
            if price <= 0 or quantity <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Price and quantity must be positive numbers.")
            # Pass the submitted data to the template
            context = {'product': product, 'categories': categories}
            return render(request, 'adminapp/edit_product.html', context)

        if Product.objects.filter(product_name=product.product_name).exclude(pk=product_id).exists():
            messages.error(request, f"A product with the name '{product.product_name}' already exists.")
            # Pass the submitted data to the template
            context = {'product': product, 'categories': categories}
            return render(request, 'adminapp/edit_product.html', context)

        # Update product details
        category = Category.objects.get(pk=category_id)
        product.category = category
        product.description = description
        product.original_price = price
        product.selling_price=price
        product.quantity = quantity

        # Handle main product image
        new_main_image = request.FILES.get('product_images')
        
        if new_main_image:
            product.product_images = new_main_image

        # Handle subimages
        new_sub_images = request.FILES.getlist('product_images')

        if new_main_image:
            product.images.all().delete()
            
        
        for image in new_sub_images:
            ProductImage.objects.create(product=product, image=image)

        product.save()
        return redirect('admin_products')

    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'adminapp/edit_product.html', context)













@login_required
def soft_delete_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return redirect('admin_products')
    product.soft_deleted = True
    product.is_available = False
    product.save()
    return redirect('admin_products')

@login_required
def undo_soft_delete_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return redirect('admin_products')
    product.soft_deleted = False
    product.is_available = True
    product.save()
    return redirect('admin_products')

#order management
@login_required
def admin_orders(request):
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    
    context = {'orders': orders}
    return render(request, 'adminapp/admin_orders.html', context)



@login_required
def update_order_status(request, order_id, new_status):
    
    order = get_object_or_404(Order, pk=order_id)
    
    if new_status == 'New':
        order.status = 'New'
    elif new_status == 'Accepted':
        order.status = 'Accepted'
    elif new_status == 'Completed':
        order.status = 'Completed'
    elif new_status == 'Cancelled':
        order.status = 'Cancelled'
    
    order.save()
    
    messages.success(request, f"Order #{order.order_number} has been updated to '{new_status}' status.")
    
    return redirect('admin_orders')




@login_required
def admin_order_details(request, order_id):
    ordersp = Order.objects.get(id=order_id)
    
    # Fetch other related data (e.g., order products, payments)
    order_products = OrderProduct.objects.filter(order=ordersp)
    #order_products = OrderProduct.objects.filter(order__user=request.user, order__id=order_id)
    orders = Order.objects.filter(is_ordered=True, id=order_id)
    
    payments = Payment.objects.filter(order__id=order_id)

    for order_product in order_products:
        order_product.total = order_product.quantity * order_product.product_price

    context = {
        'order_products': order_products,
        'orders': orders,
        'payments': payments,
    }

    return render(request, 'adminapp/admin_order_details.html', context)


@login_required
def admin_order_detailss(request, order_id):
    # Fetch the specific order based on the order_id
    orders = Order.objects.get(id=order_id)
    
    # Fetch other related data (e.g., order products, payments)
    order_products = OrderProduct.objects.filter(order=orders)
    payments = Payment.objects.filter(order=orders)

    for order_product in order_products:
        order_product.total = order_product.quantity * order_product.product_price

    context = {
        'orders': orders,
        'order_products': order_products,
        'payments': payments,
    }

    return render(request, 'adminapp/admin_order_details.html', context)



@login_required
def admin_coupons(request):
    if request.user.is_superuser:
        coupons = Coupons.objects.all()
        context = {'coupons': coupons}
        return render(request, 'adminapp/admin_coupons.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")

@login_required
def add_coupons(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        description = request.POST.get('description')
        minimum_amount = request.POST.get('minimum_amount')
        discount = request.POST.get('discount')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')

        try:
            minimum_amount = int(minimum_amount)
            discount = int(discount)
        except ValueError:
            messages.error(request, "Minimum Amount and Discount must be integers.")
            return redirect('add_coupons')

        coupon = Coupons(
            coupon_code=coupon_code,
            description=description,
            minimum_amount=minimum_amount,
            discount=discount,
            valid_from=valid_from,
            valid_to=valid_to
        )
        coupon.save()
        messages.success(request, "Coupon added successfully.")
        return redirect('admin_coupons')

    return render(request, 'adminapp/add_coupons.html')




@login_required
def edit_coupons(request, coupon_id):
    try:
        coupon = Coupons.objects.get(pk=coupon_id)
    except Coupons.DoesNotExist:
        return redirect('admin_coupons')

    if request.method == 'POST':
        coupon.coupon_code = request.POST.get('coupon_code')
        coupon.description = request.POST.get('description')
        coupon.minimum_amount = int(request.POST.get('minimum_amount'))
        coupon.discount = int(request.POST.get('discount'))
        coupon.valid_from = request.POST.get('valid_from')
        coupon.valid_to = request.POST.get('valid_to')
        
        coupon.save()
        
        return redirect('admin_coupons')

    context = {'coupon': coupon}
    return render(request, 'adminapp/edit_coupons.html', context)




@login_required
def delete_coupons(request, coupon_id):
    try:
        coupon = Coupons.objects.get(pk=coupon_id)
    except Coupons.DoesNotExist:
        return redirect('admin_coupons')

    if request.method == 'POST':
        coupon.delete()
        messages.success(request, "Coupon deleted successfully.")
    
    return redirect('admin_coupons')



def sales_report(request):
    sales_report = Order.objects.all()  # Replace with your actual query
    #sales_report = Order.objects.filter(is_ordered=True)
    return render(request, 'adminapp/sales_reports.html', {'sales_report': sales_report})

def cancel_report(request):
    search_keyword = request.GET.get('search')
    cancelled_orders = Order.objects.filter(status='Cancelled')
    
    if search_keyword:
        cancelled_orders = cancelled_orders.filter(user__first_name__icontains=search_keyword)
    
    return render(request, 'adminapp/cancel_report.html', {'cancelled_orders': cancelled_orders})

def stock_report(request):
    stock = Product.objects.all()
    context={
        'stock':stock,
    }

    return render(request,'adminapp/stock_report.html',context)