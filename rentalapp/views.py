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

# Home Page
def home(request):
    try:
        featured_products = Product.objects.filter(is_featured=True)[:3]
        products = Product.objects.all()
        for product in products:
            print(f"DEBUG: Product ID {product.id}, Sizes: {product.sizes}")
        gallery_images = [
            "1.1.png",
            "Accessories.png",
            "Beach-Day.png",
            "Gentlewoman-Waistband.png",
            "Sister-JINNY-TO.png",
            "Unigam-BEBBY-TOP.png"
        ]
        context = {
            'welcome_message': 'Welcome to the Fashion Rental Platform!',
            'featured_products': featured_products,
            'gallery_images': gallery_images,
            'products': products,
        }
        return render(request, 'rental/base.html', context)
    except TypeError as e:
        print(f"ERROR: {e}")  # Log the error for debugging
        return render(request, 'rental/error.html', {'message': 'Invalid product data encountered.'})

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

# Checkout
@login_required
def checkout(request, checkout_id):
    checkout = get_object_or_404(Checkout, id=checkout_id, user=request.user)

    if request.method == "POST":
        # Confirm the rental and update the product availability
        checkout.is_confirmed = True
        checkout.save()

        product = checkout.product
        product.is_available = False
        product.save()

        messages.success(request, f"คุณเช่าสินค้า {product.name} เป็นเวลา {checkout.rent_days} วันเรียบร้อยแล้ว!")
        return redirect('rental_history')

    return render(request, 'rental/checkout.html', {'checkout': checkout})

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



# How To Rent
def how_to_rent(request):
    return render(request, 'rental/how_to_rent.html')

# Profile (CBV)
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'rental/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

# Product Views
# Product Views
from django.shortcuts import render
from .models import Product

from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()

    # Get unique colors and sizes from the database
    colors = set()
    sizes = set()
    for product in products:
        if product.colors:
            colors.update(product.colors)
        if product.sizes:
            sizes.update(product.sizes)

    # Apply filters
    category = request.GET.get('category')
    if category:
        products = products.filter(category_id=category)

    status = request.GET.get('status')
    if status:
        products = products.filter(status=status)

    color = request.GET.get('color')
    if color:
        products = products.filter(colors__contains=[color])

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

    return render(request, 'rental/product_list.html', {
        'products': products,
        'colors': colors,
        'sizes': sizes,
    })
    # Filter for featured products for a separate section
    featured_products = Product.objects.filter(is_featured=True, is_active=True)

    return render(request, 'rental/product_list.html', {
        'products': products,
        'featured_products': featured_products,
    })

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


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Product
@login_required

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        # Check stock availability
        if not product.is_in_stock(quantity):
            messages.error(request, "Not enough stock available.")
            return redirect("product_detail", product_id=product.id)

        # Add product to cart (example cart logic)
        cart = request.session.get("cart", {})
        if product_id in cart:
            cart[product_id]["quantity"] += quantity
        else:
            cart[product_id] = {"quantity": quantity, "name": product.name, "price": float(product.price)}

        # Save updated cart in session
        request.session["cart"] = cart

        # Reduce stock
        product.reduce_stock(quantity)

        messages.success(request, f"{product.name} added to cart.")
        return redirect("product_detail", product_id=product.id)


@login_required
def cart(request):
    session_cart = request.session.get('cart', {})
    cart_items = []
    for product_id, item in session_cart.items():
        try:
            product = Product.objects.get(id=product_id)
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': item['price'],
                'image': product.image.url if product.image else None,
                'quantity': item['quantity'],
                'total_price': float(item['price']) * item['quantity']
            })
        except Product.DoesNotExist:
            continue
    return render(request, 'rental/cart.html', {'cart_items': cart_items})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Item not found in cart'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# Checkout
@login_required
def checkout_view(request):
    cart = Cart.objects.get(user=request.user)
    return render(request, 'rental/checkout.html', {'cart': cart})

# Rent Now
from django.contrib import messages
from .models import Product, Checkout

@login_required
def rent_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rent_days = int(request.POST.get("rent_days", 1))

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

# Rental History
@login_required
def rental_history(request):
    rentals = Rental.objects.filter(user=request.user).order_by('-rental_date')
    return render(request, 'rental/rental_history.html', {'rentals': rentals})

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