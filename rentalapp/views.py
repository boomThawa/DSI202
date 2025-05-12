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

# Cart Views
from decimal import Decimal
from django.http import JsonResponse

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

        return JsonResponse({'success': True, 'subtotal': float(subtotal), 'total': float(total)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

from django.shortcuts import render
from .models import Product
from django.shortcuts import render
from .models import Cart, CartItem

def view_cart(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            total_price = sum(item.total_price() for item in cart_items)

            context = {
                'cart_items': cart_items,
                'total_price': total_price,
                'subtotal': total_price, # โดยทั่วไป Subtotal จะเท่ากับ Total ในกรณีที่ไม่มีส่วนลด/ค่าส่ง
            }
            return render(request, 'rentalapp/cart.html', context)
        except Cart.DoesNotExist:
            context = {
                'cart_items': [],
                'total_price': 0,
                'subtotal': 0,
            }
            return render(request, 'rentalapp/cart.html', context)
    else:
        # Handle กรณีผู้ใช้ไม่ได้ Login (อาจจะ Redirect ไปหน้า Login หรือแสดง Cart จาก Session)
        # สำหรับตัวอย่างนี้ จะส่ง Cart ว่าง
        context = {
            'cart_items': [],
            'total_price': 0,
            'subtotal': 0,
        }
        return render(request, 'rentalapp/cart.html', context)

    

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Product

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem
from django.utils import timezone

def add_to_cart(request, product_id):
    # ดึงสินค้า
    product = Product.objects.get(id=product_id)
    
    # ตรวจสอบว่าผู้ใช้มี Cart หรือยัง
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # รับข้อมูลจากฟอร์ม
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))
    start_date = request.POST.get('start_date')
    rent_days = int(request.POST.get('rent_days', 1))
    return_date = request.POST.get('return_date')
    return_date=return_date if return_date else None  # ตั้งค่าเป็น None ถ้าไม่มีค่า


    # สร้าง CartItem ใหม่
    cart_item = CartItem(cart=cart, product=product, quantity=quantity, size=size, start_date=start_date, rent_days=rent_days, return_date=return_date)
    cart_item.save()
    
    # รีไดเร็กไปที่หน้าตะกร้าสินค้า
    return redirect('cart')

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CartItem

def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=item_id)
        cart_item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'ลบสินค้าไม่สำเร็จ'}, status=400)


def checkout(request):
    # 1. ตรวจสอบการเข้าสู่ระบบของผู้ใช้
    if not request.user.is_authenticated:
        return redirect('login')

    order_id = request.session.get('order_id')
    order = None

    if not order_id:
        # สร้าง Order ใหม่และบันทึกเพื่อรับ id
        order = Order.objects.create(
            user=request.user,
            total_price=0.00,  # อ้างอิงจากข้อมูล SQL
            created_at=timezone.now(),
            status='pending' # อ้างอิงจากข้อมูล SQL
            # เพิ่มฟิลด์อื่นๆ ที่จำเป็น
        )
        request.session['order_id'] = order.id
    else:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "ไม่พบรายการสั่งซื้อของคุณ")
            return redirect('cart')

    checkout_data = request.session.get('checkout_data', {})
    if not checkout_data:
        messages.error(request, "ไม่มีข้อมูลการชำระเงิน")
        return redirect('cart')

    cart_items = checkout_data.get('cart_items', [])
    subtotal = checkout_data.get('subtotal', 0)
    total = checkout_data.get('total', 0)

    # อัปเดต total_price ของ order (ถ้าจำเป็น)
    order.total_price = total
    order.save()

    return render(request, 'rental/checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'order': order,
    })


from django.shortcuts import render, redirect, get_object_or_404
from .models import Order

def checkout_view(request):
    # เช็คว่าผู้ใช้ล็อกอินหรือยัง
    if not request.user.is_authenticated:
        return redirect('login')  # ถ้ายังไม่ล็อกอิน ให้ไปหน้า login

    # เช็คว่ามีสินค้าในตะกร้าหรือไม่
    if not cart_has_items(request):
        return redirect('cart')  # ถ้าไม่มีสินค้าในตะกร้า ให้ไปที่หน้าตะกร้า

    # ดึง order_id จาก session
    order_id = request.session.get('order_id')
    
    if order_id:
        # ถ้าพบ order_id ให้ดึง order จากฐานข้อมูล
        order = get_object_or_404(Order, id=order_id)
        
        # คุณสามารถคำนวณ total ได้ตาม logic ของคุณเอง
        # ตัวอย่างนี้ใช้ฟิลด์ total_price จากโมเดล (ต้องแน่ใจว่ามีใน Order model)
        total = order.total_price if hasattr(order, 'total_price') else 0
        
        return render(request, 'checkout.html', {
            'order': order,
            'total': total,
        })
    else:
        # ถ้าไม่พบ order_id ใน session ให้ redirect ไปยังหน้าหลักหรือหน้าที่เหมาะสม
        return redirect('home')  # เปลี่ยนเป็นชื่อ path ที่เหมาะสม

# ฟังก์ชันตรวจสอบว่าตะกร้ามีสินค้าหรือไม่
def cart_has_items(request):
    # สมมติว่า cart ของคุณเก็บใน session, ตรวจสอบให้มี items ใน cart
    cart = request.session.get('cart', {})
    return len(cart) > 0


from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Product, Checkout

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





from .models import Cart, CartItem, Checkout, Product

def process_checkout(request):
    cart = get_object_or_404(Cart, user=request.u_ser)
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        product = item.product
        discount_price = product.price - (product.price * (product.discount / 100))
        total_price = discount_price * item.quantity * item.rent_days

        Checkout.objects.create(
            user=request.user,
            product=product,
            rent_days=item.rent_days,
            total_price=total_price,
            created_at=timezone.now(),
            is_confirmed=False,
            status='pending'
        )

    cart_items.delete()
    cart.delete()

    return redirect('checkout_success')  # หรือหน้า payment

from django.shortcuts import render, get_object_or_404
from .models import Order

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    checkout_data = request.session.get('checkout_data', {})
    total = checkout_data.get('total', 0)  # ดึงยอดรวมจาก session

    return render(request, 'rental/payment.html', {'order': order, 'total': total})


from .models import Order
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Rental, Cart, CartItem
from django.utils import timezone

@login_required
def payment_success_handler(request): # สมมติว่านี่คือ View ที่จัดการเมื่อชำระเงินสำเร็จ
    checkout_data = request.session.get('checkout_data')

    if checkout_data and checkout_data.get('cart_items'):
        rental = Rental.objects.create(
            user=request.user,
            start_date=timezone.now().date(), # หรือวันที่เริ่มต้นเช่าจริง
            total_price=checkout_data.get('total', 0), # ดึงราคารวมจาก Session
            # ดึงข้อมูลอื่นๆ จาก cart_items หรือ checkout_data
        )

        for item in checkout_data['cart_items']:
            product = Product.objects.get(id=item['id'])
            rental.product = product
            rental.size = item.get('size', '') # ดึงขนาด (ถ้ามี)
            rental.color = item.get('color', '') # ดึงสี (ถ้ามี)
            rental.rent_days = item.get('quantity', 1) # ดึงจำนวนวันเช่า (ใช้ quantity เป็นจำนวนวันเช่า)
            rental.save() # บันทึกแต่ละสินค้าเป็นการเช่า

        # ล้างตะกร้าสินค้าหลังจากบันทึกประวัติการเช่า
        request.session['cart'] = {}
        del request.session['checkout_data']

        messages.success(request, "การชำระเงินเสร็จสมบูรณ์! ระบบได้บันทึกประวัติการเช่าของคุณแล้ว")
        return redirect('rental_history') # Redirect ไปยังหน้าประวัติการเช่า

    else:
        messages.error(request, "ไม่พบข้อมูลการเช่า")
        return redirect('cart') # หรือหน้าที่เหมาะสม
    
# Assuming CartItem is linked to the Rental through a Foreign Key
@login_required
def check_payment(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        if order_id:
            try:
                order = get_object_or_404(Order, id=order_id, user=request.user)
                cart = Cart.objects.get(user=request.user)
                cart_items = cart.cartitem_set.all()

                # Create Rental object with a pending payment status
                rental = Rental.objects.create(
                    user=request.user,
                    order=order,  # Associate the rental with the order
                    start_date=timezone.now().date(),
                    total_price=order.total_price,
                    is_payment_verified=False,
                )

                # Link cart items to the rental
                for item in cart_items:
                    RentalItem.objects.create(  # Assuming RentalItem holds the same fields as CartItem
                        rental=rental,
                        product=item.product,
                        quantity=item.quantity,
                        rent_days=item.rent_days,
                        start_date=item.start_date,
                    )

                # Optionally clear the cart
                cart_items.delete()
                request.session.pop('order_id', None)

                messages.info(request, "Your payment is pending verification.")
                return redirect('rental_history')  # Redirect to rental history or payment pending page

            except Order.DoesNotExist:
                messages.error(request, "Order not found.")
                return redirect('cart')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('cart')
        else:
            messages.error(request, "Order ID not provided.")
            return redirect('cart')
    else:
        return redirect('cart')

# rentalapp/views.py
from django.shortcuts import render

from .models import Rental  # สมมติว่ามี Model ชื่อ Rental
from django.shortcuts import render
from .models import Rental

def rental_history(request):
    if request.user.is_authenticated:
        history_data = Rental.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'rental/rental_history.html', {'history_items': history_data})
    else:
        return render(request, 'rental/login_required.html')