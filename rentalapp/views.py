from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import Product, Outfit, Trend
from math import floor
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

# Login View
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/Users/thawaphorn/Desktop/dsi202-final/rental/rentalapp/templates/rental/base.html')  # เปลี่ยนเป็น URL ของหน้าแรกที่ต้องการ
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, "rental/login.html", {"form": form})

from django.shortcuts import redirect
from django.contrib.auth import logout

def logout_view(request):
    logout(request)  # ออกจากระบบ
    return redirect('login')  # เปลี่ยนเส้นทางไปที่หน้าล็อกอินหลังจากออกจากระบบ

from django.shortcuts import redirect, get_object_or_404
from .models import Product, Cart

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        # เพิ่มสินค้าในตะกร้า
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.products.add(product)
        return redirect('cart')

def rent_now(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        # สมมุติว่าคุณมีโมเดล RentalSession หรือ TemporaryCart
        request.session['rent_now_product_id'] = product.id
        return redirect('checkout')  # หรือใช้ 'payment' / 'confirm_rent' ตามที่คุณตั้งชื่อ
from .models import Cart, CartItem, Product
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity += 1
    item.save()
    return redirect('cart')

# model.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r'^\+?(\d{1,4})?[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}$')])
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'rentalapp'

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=20, unique=True, blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # ตรวจสอบว่า slug ซ้ำหรือไม่
        existing_slug = Product.objects.filter(slug=self.slug).aggregate(Max('id'))['id__max']
        if existing_slug:
            self.slug = f"{self.slug}-{existing_slug + 1}"
        if self.stock == 0:
            self.status = 'out_of_stock'
        elif self.status != 'discontinued':
            self.status = 'available'
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class Outfit(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    size = models.CharField(max_length=20)
    image = models.ImageField(upload_to='outfits/')
    description = models.TextField()

    def clean(self):
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    outfits = models.ManyToManyField(Outfit, related_name='orders')
    total_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class Return(models.Model):
    RETURN_METHOD_CHOICES = [
        ('store', 'คืนที่ร้าน'),
        ('pickup', 'รับที่บ้าน'),
    ]

    RETURN_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('completed', 'Completed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    method = models.CharField(max_length=100, choices=RETURN_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=RETURN_STATUS_CHOICES, default='pending')
    review = models.TextField(blank=True, help_text="Please provide your feedback or reason for return.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return for Order #{self.order.id}"


class Trend(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='trends/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class OrderOutfit(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=20)

    class Meta:
        unique_together = ('order', 'outfit')

    def __str__(self):
        return f"{self.quantity} of {self.outfit.name} in size {self.size}"

from django.db import models
from django.contrib.auth.models import User
from rentalapp.models import Product

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"{self.user.username}'s Cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    rent_days = models.PositiveIntegerField(default=3)  # กำหนดค่าเริ่มต้น 3 วัน

    def total_price(self):
        return self.product.price * self.quantity * self.rent_days

    def __str__(self):
        return f"{self.product.name} × {self.quantity} ({self.rent_days} days)"

@login_required
def invoice(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    return render(request, 'rental/invoice.html', {'rental': rental})

@login_required
def rent_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.session['rent_now_product_id'] = product.id
    return redirect('checkout')

@login_required
def update_rent_days(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        new_days = int(request.POST.get('rent_days', item.rent_days))
        item.rent_days = new_days
        item.save()
    return redirect('cart')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'rentalapp/cart.html', {'cart': cart})

@login_required
def checkout_view(request):
    product_id = request.session.get('rent_now_product_id')
    product = get_object_or_404(Product, id=product_id) if product_id else None
    return render(request, 'rentalapp/checkout.html', {'product': product})

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def return_request(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    if request.method == 'POST' and not rental.returned:
        rental.returned = True
        rental.return_date = timezone.now()
        rental.save()
        messages.success(request, 'ระบบได้รับคำขอคืนสินค้าเรียบร้อยแล้ว')
    return redirect('rental_history')

@login_required
def return_request(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    if request.method == 'POST' and rental.return_status == 'not_requested':
        rental.return_status = 'pending'
        rental.save()
        messages.success(request, 'ส่งคำขอคืนสินค้าเรียบร้อยแล้ว กำลังรอการอนุมัติ')
    return redirect('rental_history')

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def manage_returns(request):
    pending_returns = Rental.objects.filter(return_status='pending')
    return render(request, 'admin/manage_returns.html', {'pending_returns': pending_returns})

@staff_member_required
def approve_return(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    rental.return_status = 'approved'
    rental.return_date = timezone.now()
    rental.save()
    messages.success(request, f'อนุมัติการคืนของ {rental.product.name} แล้ว')
    return redirect('manage_returns')

@staff_member_required
def reject_return(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    rental.return_status = 'rejected'
    rental.save()
    messages.error(request, f'ปฏิเสธการคืนของ {rental.product.name}')
    return redirect('manage_returns')
 
@login_required
def rental_history(request):
    rentals = Rental.objects.filter(user=request.user).order_by('-rental_date')
    return render(request, 'rental/rental_history.html', {'rentals': rentals})

# Home Page
def home(request):
    featured_products = Product.objects.filter(is_featured=True)[:3]
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
    }
    return render(request, 'rental/base.html', context)
from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # เปลี่ยนเป็น URL name ที่คุณใช้
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# Profile Page
@login_required
def profile(request):
    return render(request, 'rental/profile.html', {'user': request.user})

# Wishlist Page (ยังต้องเพิ่ม logic)
@login_required
def wishlist(request):
    return render(request, 'rental/wishlist.html')

# Product List Page with Search and Category Filter
def product_list(request):
    products = Product.objects.all()
    category = request.GET.get('category')
    if category:
        products = products.filter(category_id=category)
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    return render(request, 'rental/product_list.html', {'products': products})

# Product Detail Page
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

# Cart Page
@login_required
def cart(request):
    cart_items = request.session.get('cart', {})
    total_price = 0
    cart_details = []

    for product_id, details in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = details.get('quantity', 1)
            rental_days = details.get('rental_days', 1)
            item_total_price = product.price * quantity * rental_days
            total_price += item_total_price
            cart_details.append({
                'product': product,
                'quantity': quantity,
                'rental_days': rental_days,
                'item_total_price': item_total_price
            })
        except Product.DoesNotExist:
            continue

    return render(request, 'rental/cart.html', {'cart_details': cart_details, 'total_price': total_price})

# Checkout Page (ยังไม่ได้เพิ่ม logic การชำระเงิน)
def checkout(request):
    if request.method == "POST":
        # เพิ่ม logic สำหรับการประมวลผลการชำระเงิน
        return redirect('checkout_complete')  # เปลี่ยนเป็น URL ที่ต้องการหลังจากเสร็จสิ้นการชำระเงิน
    return render(request, 'checkout.html')

# Outfit Detail View
class OutfitDetailView(DetailView):
    model = Outfit
    template_name = 'outfit_detail.html'
    context_object_name = 'outfit'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj is None:
            raise Http404("Outfit not found")
        return obj

# About Us Page
def about_us(request):
    return render(request, 'rental/about_us.html')

# Outfit Search
def outfit_search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Outfit.objects.filter(name__icontains=query)  # หรือจะใช้ description ด้วยก็ได้

    return render(request, 'rental/outfit_search.html', {
        'results': results,
        'query': query
    })

# Return Outfit Page
def return_outfit(request):
    return render(request, 'return.html', {'message': 'Return item form goes here'})

# Category List Page
def category_list(request):
    categories = [
        {"name": "ชุดเดรส", "image": "https://source.unsplash.com/100x100/?dress"},
        {"name": "เสื้อ", "image": "https://source.unsplash.com/100x100/?shirt"},
        {"name": "กระโปรง", "image": "https://source.unsplash.com/100x100/?skirt"},
        {"name": "กางเกง", "image": "https://source.unsplash.com/100x100/?pants"},
    ]
    return render(request, 'rental/category_list.html', {'categories': categories})

# How To Rent Page
def how_to_rent(request):
    return render(request, 'rental/how_to_rent.html')

# Account Page
def account(request):
    return render(request, 'rental/account.html')

# Trend List Page
def trend_list(request):
    trends = Trend.objects.all()
    return render(request, 'rental/trend_list.html', {'trends': trends})
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone

# สำหรับอนุมัติการคืน
@login_required
@staff_member_required
def approve_return(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    rental.return_status = 'approved'
    rental.return_date = timezone.now()
    rental.save()

    # แจ้งเตือนผู้ใช้ผ่าน email
    send_mail(
        'สินค้าของคุณได้รับการอนุมัติคืน',
        f'สวัสดี {rental.user.username},\n\nการคืนสินค้า "{rental.product.name}" ของคุณได้รับการอนุมัติแล้ว! ขอขอบคุณที่ใช้บริการของเรา',
        'no-reply@rentyourstyle.com',
        [rental.user.email],
        fail_silently=False,
    )

    # แจ้งเตือนแอดมิน
    messages.success(request, f'อนุมัติการคืนของ {rental.product.name} แล้ว')
    return redirect('manage_returns')

# สำหรับปฏิเสธการคืน
@login_required
@staff_member_required
def reject_return(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    rental.return_status = 'rejected'
    rental.save()

    # แจ้งเตือนผู้ใช้ผ่าน email
    send_mail(
        'การคืนสินค้าของคุณถูกปฏิเสธ',
        f'สวัสดี {rental.user.username},\n\nการคืนสินค้า "{rental.product.name}" ของคุณถูกปฏิเสธ เนื่องจากปัญหาที่เกี่ยวข้องกับการตรวจสอบสินค้าของเรา',
        'no-reply@rentyourstyle.com',
        [rental.user.email],
        fail_silently=False,
    )

    # แจ้งเตือนแอดมิน
    messages.error(request, f'ปฏิเสธการคืนของ {rental.product.name}')
    return redirect('manage_returns')
