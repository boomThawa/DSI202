from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.generic import DetailView
from .models import Product, Category, Cart, CartItem, Rental, UserProfile, Outfit, Trend
from math import floor
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from .models import Category
from django.shortcuts import render, get_object_or_404, redirect
# ... imports อื่นๆ ...

# Invoice
@login_required
def invoice(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    return render(request, 'rental/invoice.html', {'rental': rental})

# Return Request
@login_required
def return_request(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    if request.method == "POST":
        rental.status = "returned"
        rental.save()
        messages.success(request, "Your return request has been submitted successfully!")
        return redirect('rental_history')
    return render(request, 'rental/return_request.html', {'rental': rental})

# Authentication Views
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.shortcuts import render
from .models import Category

def category_images(request):
    categories = Category.objects.all()
    return render(request, 'rental/category_images.html', {'categories': categories})

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'rental/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
# Wishlist
@login_required
def wishlist(request):
    wishlist_items = []  # Example placeholder for Wishlist data
    return render(request, 'rental/wishlist.html', {'wishlist_items': wishlist_items})


# Return Outfit
@login_required
def return_outfit(request):
    if request.method == "POST":
        messages.success(request, "Your outfit return request has been submitted.")
        return redirect('rental_history')
    return render(request, 'rental/return_outfit.html')

# Account
@login_required
def account(request):
    user = request.user
    return render(request, 'rental/account.html', {'user': user})

# Category List
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'rental/category_list.html', {'categories': categories})

# Outfit Search
def outfit_search(request):
    query = request.GET.get('q')
    results = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'rental/outfit_search.html', {'query': query, 'results': results})

# Home Page
from django.shortcuts import render
from .models import Product

def home(request):
    # ดึงสินค้าที่ถูกกำหนดให้เป็นสินค้ายอดนิยม (Featured Products)
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)[:3]
    
    # ตรวจสอบและเตรียมข้อมูลสินค้าที่จะแสดงใน Template
    for product in featured_products:
        # ตรวจสอบว่าฟิลด์ sizes มีค่าหรือไม่
        if not product.sizes:
            product.sizes = []  # กำหนดค่าเริ่มต้นเป็น list ว่าง
        elif isinstance(product.sizes, str):  # กรณี sizes เป็น string (JSON string)
            try:
                import json
                product.sizes = json.loads(product.sizes)  # แปลงเป็น Python list
            except json.JSONDecodeError:
                product.sizes = []  # หาก JSON ไม่ถูกต้อง ให้กำหนดเป็น list ว่าง

    # กำหนดภาพสำหรับแกลเลอรี
    gallery_images = [
        "1.1.png",
        "Accessories.png",
        "Beach-Day.png",
        "Gentlewoman-Waistband.png",
        "Sister-JINNY-TO.png",
        "Unigam-BEBBY-TOP.png"
    ]

    # ส่งข้อมูลไปยัง Template
    context = {
        'welcome_message': 'Welcome to the Fashion Rental Platform!',
        'featured_products': featured_products,
        'gallery_images': gallery_images,
        'categories': categories,
    }
    return render(request, 'rental/base.html', context)


# How To Rent
def how_to_rent(request):
    return render(request, 'rental/how_to_rent.html')


# Product Views
from django.shortcuts import render
from django.http import JsonResponse
from .models import Product

def product_list(request):
    try:
        # ดึงข้อมูลสินค้าทั้งหมด
        products = Product.objects.all()
        sizes = set()
        
        # ตรวจสอบและจัดการข้อมูล JSONField สำหรับ sizes
        for product in products:
            if product.sizes and isinstance(product.sizes, list):
                sizes.update(product.sizes)

        # Apply filters
        category = request.GET.get('category')
        if category:
            products = products.filter(category_id=category)

        status = request.GET.get('status')
        if status:
            products = products.filter(status=status)

        size = request.GET.get('size')
        if size:
            products = products.filter(sizes__contains=[size])

        search_query = request.GET.get('search')
        if search_query:
            products = products.filter(name__icontains=search_query)

        # Apply sorting
        sort_by = request.GET.get('sort')
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('name')
        elif sort_by == 'name_desc':
            products = products.order_by('-name')
        elif sort_by == 'rating_asc':
            products = products.order_by('rating')
        elif sort_by == 'rating_desc':
            products = products.order_by('-rating')

        # Filter for featured products
        featured_products = Product.objects.filter(is_featured=True, is_active=True)

        # Render the template with context data
        return render(request, 'rental/product_list.html', {
            'products': products,
            'sizes': sizes,
            'featured_products': featured_products,
        })

    except TypeError as e:
        # จัดการข้อผิดพลาด TypeError
        print(f"Error: {e}")
        return JsonResponse({"error": "Invalid product data encountered."}, status=500)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    full_stars = [1] * floor(product.rating)
    half_star = product.rating - floor(product.rating) >= 0.5
    empty_stars = 5 - len(full_stars) - (1 if half_star else 0)
    empty_stars = [1] * empty_stars
    return render(request, 'rental/product_detail.html', {
        'product': product,
        'full_stars': full_stars,
        'half_star': half_star,
        'empty_stars': empty_stars
    })


from django.shortcuts import render, redirect, get_object_or_404
from .models import Order


# ฟังก์ชันตรวจสอบว่าตะกร้ามีสินค้าหรือไม่
def cart_has_items(request):
    # สมมติว่า cart ของคุณเก็บใน session, ตรวจสอบให้มี items ใน cart
    cart = request.session.get('cart', {})
    return len(cart) > 0


from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

@login_required
def rent_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rent_days = request.POST.get("rent_days", "")

        # ตรวจสอบว่า rent_days เป็นตัวเลขหรือไม่ ถ้าไม่เป็นตัวเลขให้ใช้ค่า default เป็น 1
        if rent_days.isdigit():
            rent_days = int(rent_days)
        else:
            rent_days = 1  # ค่า default ถ้าไม่ได้รับข้อมูลที่เป็นตัวเลข

        # ตรวจสอบว่าสินค้ามีให้เช่าหรือไม่
        if not product.is_available:
            messages.error(request, "สินค้านี้ไม่พร้อมให้เช่า")
            return redirect('product_detail', product_id=product.id)

        # คำนวณราคาทั้งหมด
        total_price = product.price * rent_days

        # สร้าง Checkout Record
        checkout = Checkout.objects.create(
            user=request.user,
            product=product,
            rent_days=rent_days,
            total_price=total_price
        )

        # Redirect ไปยังหน้าชำระเงินหรือยืนยันการเช่า
        return redirect('checkout', checkout_id=checkout.id)

    return render(request, 'rental/product_detail.html', {'product': product})


# Update Rent Days
@login_required
def update_rent_days(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == "POST":
        new_rent_days = int(request.POST.get("rent_days", cart_item.rent_days))
        cart_item.rent_days = new_rent_days
        cart_item.total_price = cart_item.product.price * new_rent_days
        cart_item.save()
        messages.success(request, "Rental days updated successfully!")
        return redirect('cart')
    return render(request, 'rental/update_rent_days.html', {'cart_item': cart_item})

# Return Management
@staff_member_required
def manage_returns(request):
    pending_returns = Rental.objects.filter(returned=False)
    return render(request, 'admin/manage_returns.html', {'pending_returns': pending_returns})

@staff_member_required
def approve_return(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    rental.returned = True
    rental.return_date = timezone.now()
    rental.save()
    messages.success(request, f'Return for rental #{rental.id} approved.')
    return redirect('manage_returns')

@staff_member_required
def reject_return(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    rental.returned = False
    rental.save()
    messages.error(request, f'Return for rental #{rental.id} rejected.')
    return redirect('manage_returns')

# Trend Views
def trend_list(request):
    trends = Trend.objects.all()
    return render(request, 'rental/trend_list.html', {'trends': trends})



def thank_you(request):
    return render(request, 'thank_you.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Order, OrderItem
from django.utils import timezone
from django.contrib import messages

from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Product, Order, OrderItem
from django.utils import timezone
from django.contrib import messages

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    size = request.POST.get('size')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    start_date = request.POST.get('start_date')
    try:
        rent_days = int(request.POST.get('rent_days', 1))
    except (ValueError, TypeError):
        rent_days = 1

    return_date = request.POST.get('return_date')
    return_date = return_date if return_date else None

    # ตรวจสอบว่าสินค้าเดิมในตะกร้ามีตัวเลือกเดียวกันหรือไม่
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        start_date=start_date,
        rent_days=rent_days,
        defaults={'quantity': quantity, 'return_date': return_date}
    )

    # ถ้ามีสินค้าเดิมอยู่แล้ว ให้เพิ่มจำนวน
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('cart')

@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')  # เพิ่มประสิทธิภาพ
        total_price = sum(item.total_price() for item in cart_items)

        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'subtotal': total_price,
        }
        return render(request, 'rentalapp/cart.html', context)
    except Cart.DoesNotExist:
        context = {
            'cart_items': [],
            'total_price': 0,
            'subtotal': 0,
        }
        return render(request, 'rentalapp/cart.html', context)

@login_required
def update_cart_quantity(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))

        cart = request.session.get('cart', {})
        product = get_object_or_404(Product, id=product_id)

        if not product.is_available:
            return JsonResponse({'success': False, 'error': 'Product is not available'})

        if quantity > product.stock:
            return JsonResponse({'success': False, 'error': f'Only {product.stock} items available'})

        if product_id in cart:
            if quantity > 0:
                cart[product_id]['quantity'] = quantity
            else:
                del cart[product_id]
        else:
            cart[product_id] = {
                'price': str(product.price),  # Store price as string to avoid serialization issues
                'quantity': quantity
            }

        request.session['cart'] = cart

        # Calculate subtotal and total
        subtotal = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
        total = subtotal  # Add delivery cost here if necessary

        return JsonResponse({'success': True, 'subtotal': float(subtotal), 'total': float(total), 'quantity': quantity})  # ส่ง quantity กลับไปด้วย

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
            cart_item.delete()
            return JsonResponse({'success': True})
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'ไม่พบสินค้าในตะกร้าของคุณ'}, status=404)
    return JsonResponse({'error': 'ลบสินค้าไม่สำเร็จ'}, status=400)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Order
from django.utils import timezone
from django.contrib import messages
from decimal import Decimal  # Import Decimal

@login_required
def checkout(request):
    try:
        # ดึง cart จาก database
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.total_price() for item in cart_items)

        # สร้าง Order ใหม่ (หรือดึง Order เก่าถ้ามี)
        order, created = Order.objects.get_or_create(
            user=request.user,
            status='pending',  # หรือสถานะเริ่มต้นที่เหมาะสม
            defaults={'total_price': total, 'created_at': timezone.now()}
        )
        if not created:
            order.total_price = total
            order.save()

        context = {
            'cart_items': cart_items,
            'total': total,
            'order': order,
        }

        # Clear cart data in session (สำคัญ!)
        request.session['cart'] = {}

        return render(request, 'rentalapp/checkout.html', context)

    except Cart.DoesNotExist:
        messages.error(request, "ไม่มีสินค้าในตะกร้า")
        return redirect('cart')

@login_required
def process_checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        messages.error(request, "ไม่มีสินค้าในตะกร้า")
        return redirect('cart')

    if request.method == 'POST':
        # สร้าง Order ใหม่
        order = Order.objects.create(
            user=request.user,
            total_price=sum(item.total_price() for item in cart_items),
            created_at=timezone.now(),
            status='pending' # หรือสถานะเริ่มต้นอื่น ๆ
        )

        # สร้าง OrderItem จาก CartItem
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                size=item.size,
                color=item.color,
                quantity=item.quantity,
                rent_days=item.rent_days,
                start_date=item.start_date
            )

        # เคลียร์ตะกร้าสินค้าหลังจากสร้าง Order แล้ว (หรืออาจจะเคลียร์หลังจากชำระเงินสำเร็จ)
        cart_items.delete()
        cart.delete()

        request.session['order_id'] = order.id # เก็บ order_id เพื่อนำไปใช้ในขั้นตอนถัดไป (เช่น ชำระเงิน)
        return redirect('checkout') # ไปยังหน้าชำระเงิน

    return redirect('cart') # ถ้าไม่ใช่ POST ให้กลับไปที่หน้าตะกร้า

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, ShippingAddress
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, ShippingAddress, Cart, CartItem  # Import Cart and CartItem

@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        # 1. รับค่าจากฟอร์มที่อยู่จัดส่ง
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address_line1 = request.POST.get('address_line1')
        address_line2 = request.POST.get('address_line2', '')
        sub_district = request.POST.get('sub_district')
        district = request.POST.get('district')
        province = request.POST.get('province')
        postal_code = request.POST.get('postal_code')

        # 2. สร้าง ShippingAddress ใหม่
        shipping_address = ShippingAddress.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            sub_district=sub_district,
            district=district,
            province=province,
            postal_code=postal_code,
            is_default=True  # หรือจะใช้ logic เช็คว่ามีที่อยู่เริ่มต้นหรือยัง
        )

        # 3. ผูกที่อยู่กับออเดอร์ (ถ้าคุณมีฟิลด์ shipping_address ใน Order)
        order.shipping_address = shipping_address
        order.save()

        # 4. TODO: ดำเนินการจ่ายเงินที่นี่ (Stripe, PromptPay หรือระบบอื่น)
        # ...

        # 5. ดึงข้อมูล cart ใหม่จาก database
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.total_price() for item in cart_items)

        # 6. ส่งไปยังหน้ายืนยันการชำระเงิน
        return render(request, 'rentalapp/payment.html', {'order': order, 'total': total, 'cart_items': cart_items})

    return redirect('checkout')  # ถ้าไม่ใช่ POST ก็กลับไป checkout


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, ShippingAddress, Cart, CartItem
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, Cart, CartItem, Rental
from django.contrib import messages

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    print(f"payment_success: order_id={order_id}, order.status={order.status}")

    if order.status == 'paid':
        print("payment_success: Order status is 'paid'")
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        print(f"payment_success: Cart items: {cart_items}")

        for item in cart_items:
            rental = Rental.objects.create(
                user=request.user,
                product=item.product,
                size=item.size,
                color=item.color,
                rent_days=item.rent_days,
                start_date=item.start_date,
                total_price=item.total_price(),
                created_at=timezone.now(),
                is_payment_verified=True
            )
            print(f"payment_success: Created rental: {rental.id}")

        cart_items.delete()
        cart.delete()
        messages.success(request, "Payment successful! Your rental has been confirmed.")
        print(f"payment_success: Redirecting to payment_success.html")
        return render(request, 'rentalapp/payment_success.html', {'order': order})
    else:
        print("payment_success: Order status is NOT 'paid', redirecting to payment_waiting")
        messages.error(request, "การชำระเงินยังไม่ได้รับการยืนยัน")
        return redirect('payment_waiting', order_id=order_id)
    


@login_required
def payment_waiting(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    response = render(request, 'rentalapp/payment_waiting.html', {'order': order})
    print(f"Response from render: {response}")
    return response

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Order
from django.contrib.auth.decorators import login_required

@login_required
def check_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return JsonResponse({'status': order.status})

@login_required
def rental_history(request):
    rentals = Rental.objects.filter(user=request.user).order_by('-created_at')
    print(f"Number of rentals found for user {request.user.id}: {rentals.count()}")
    return render(request, 'rentalapp/history.html', {'rentals': rentals})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'rental/order_detail.html', {'order': order})


from .models import Order, Review
from .forms import ReviewForm

@login_required
def leave_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.order = order
            review.save()
            return redirect('order_history')  # หลังจากรีวิวเสร็จจะไปที่หน้าประวัติการสั่งซื้อ
    else:
        form = ReviewForm()
    return render(request, 'rental/leave_review.html', {'form': form, 'order': order})

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def send_payment_status_update_email(sender, instance, created, **kwargs):
    if instance.status == 'paid':  # ใช้ status แทน payment_status
        # ส่งอีเมลหรือทำการอื่น ๆ ตามที่ต้องการ
        pass


from django.shortcuts import render
from .models import Order, Product
from django.contrib.auth.decorators import login_required

@login_required
def user_dashboard(request):
    # ดึงข้อมูลคำสั่งซื้อและสินค้าที่ผู้ใช้เช่า
    orders = Order.objects.filter(user=request.user)
    rented_products = Product.objects.filter(order__user=request.user)

    return render(request, 'dashboard.html', {
        'orders': orders,
        'rented_products': rented_products,
    })

from django.shortcuts import render
from .forms import ReviewForm

def create_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()  # บันทึกรีวิวลงในฐานข้อมูล
            return redirect('success')  # เปลี่ยนเป็นเส้นทางที่ต้องการหลังจากบันทึกสำเร็จ
    else:
        form = ReviewForm()

    return render(request, 'create_review.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, Review
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required

@login_required
def review(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user:
        return redirect('home')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.order = order
            review.save()
            return redirect('review', order_id=order.id)
    else:
        form = ReviewForm()

    # เพิ่มตรงนี้: ดึงออร์เดอร์ทั้งหมดของผู้ใช้
    orders = Order.objects.filter(user=request.user)

    return render(request, 'rentalapp/review.html', {
        'order': order,
        'form': form,
        'orders': orders,  # เพิ่มใน context
    })

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CartItem

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rental, CartItem
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rental, CartItem  # Import โมเดลที่เกี่ยวข้อง
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CartItem, Rental
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Rental
from django.utils import timezone

@login_required
def confirm_rental(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        messages.error(request, "ไม่มีสินค้าในตะกร้าสำหรับการเช่า")
        return redirect('cart')

    if request.method == 'POST':
        # Logic การชำระเงิน (สมมติว่าสำเร็จ)
        # ...

        for item in cart_items:
            Rental.objects.create(
                user=request.user,
                product=item.product,
                size=item.size,
                color=item.color,
                rent_days=item.rent_days,
                start_date=item.start_date,
                total_price=item.total_price(),
                created_at=timezone.now(),
                is_payment_verified=True # หรือตามสถานะการชำระเงินจริง
            )

        # เคลียร์ตะกร้าสินค้าหลังจากสร้าง Rental แล้ว
        cart_items.delete()
        cart.delete()

        messages.success(request, "การเช่าของคุณสำเร็จแล้ว!")
        return redirect('rental_history')

    return render(request, 'rental/confirm_rental.html') # หรือ Template อื่นๆ


@receiver(post_save, sender=Rental)
def clear_cart_after_rental(sender, instance, created, **kwargs):
    if created:
        # ลบสินค้าทั้งหมดในตะกร้าของผู้ใช้หลังจากมีการเช่า
        CartItem.objects.filter(cart__user=instance.user).delete()
        # ไม่ต้องสร้าง Rental ซ้ำที่นี่ Rental ถูกสร้างไปแล้ว

from .models import Rental
from django.utils import timezone

def create_rental(user, product, size, color, rent_days, start_date, total_price):
    rental = Rental.objects.create(
        user=user,
        product=product,
        size=size,
        color=color,
        rent_days=rent_days,
        start_date=start_date,
        total_price=total_price,
        created_at=timezone.now(),
        is_payment_verified=False,  # เริ่มต้นเป็น False จนกว่าจะมีการยืนยันการชำระเงิน
    )
    return rental

from django.shortcuts import render

def return_policy_view(request):
    return render(request, 'rentalapp/return_policy.html')

from django.shortcuts import render


    
from django.shortcuts import render
from .models import Order

def us_view(request):
    order_count = Order.objects.all().count()
    context = {'order_count': order_count}
    return render(request, 'rentalapp/us.html', context)
from django.shortcuts import render
from .models import Order
