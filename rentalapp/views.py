from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import Product, Outfit, Trend
from math import floor

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

@login_required
def profile(request):
    return render(request, 'rental/profile.html', {'user': request.user})

@login_required
def wishlist(request):
    # TODO: เพิ่ม logic ดึงข้อมูล wishlist ของผู้ใช้จากฐานข้อมูล
    return render(request, 'rental/wishlist.html')

class OutfitDetailView(DetailView):
    model = Outfit
    template_name = 'outfit_detail.html'
    context_object_name = 'outfit'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj is None:
            raise Http404("Outfit not found")
        return obj

def about_us(request):
    return render(request, 'rental/about_us.html')

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

def outfit_search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Outfit.objects.filter(name__icontains=query)  # หรือจะใช้ description ด้วยก็ได้

    return render(request, 'rental/outfit_search.html', {
        'results': results,
        'query': query
    })

def checkout(request):
    if request.method == "POST":
        # TODO: เพิ่ม logic สำหรับการประมวลผลการชำระเงิน
        return redirect('checkout_complete')
    return render(request, 'checkout.html')

def return_outfit(request):
    return render(request, 'return.html', {'message': 'Return item form goes here'})

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

def category_list(request):
    categories = [
        {"name": "ชุดเดรส", "image": "https://source.unsplash.com/100x100/?dress"},
        {"name": "เสื้อ", "image": "https://source.unsplash.com/100x100/?shirt"},
        {"name": "กระโปรง", "image": "https://source.unsplash.com/100x100/?skirt"},
        {"name": "กางเกง", "image": "https://source.unsplash.com/100x100/?pants"},
    ]
    return render(request, 'rental/category_list.html', {'categories': categories})

def how_to_rent(request):
    return render(request, 'rental/how_to_rent.html')

def account(request):
    return render(request, 'rental/account.html')

def product_list(request):
    products = Product.objects.all()
    category = request.GET.get('category')
    if category:
        products = products.filter(category_id=category)
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    return render(request, 'rental/product_list.html', {'products': products})

def trend_list(request):
    trends = Trend.objects.all()
    return render(request, 'rental/trend_list.html', {'trends': trends})