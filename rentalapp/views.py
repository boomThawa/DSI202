# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.http import Http404
from .models import Product, Outfit, Trend
from .models import Product  # เพิ่มบรรทัดนี้เพื่อ import โมเดล Product
from django.db import models


def home(request):
    # ใช้ Product.objects.filter() เพื่อกรองสินค้าที่มีการตั้งค่าเป็น featured
    
    featured_products = Product.objects.all()[:3]

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


def wishlist(request):
    # แสดงรายการสินค้าที่ถูกเพิ่มใน wishlist
    return render(request, 'rental/wishlist.html')  # เปลี่ยนเป็นไฟล์ template ที่ต้องการ

# หน้าแสดงรายละเอียด Outfit
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
    return render(request, 'rental/about_us.html')  # เปลี่ยนเป็นไฟล์ template ที่คุณต้องการ

# ฟังก์ชันการแสดงตะกร้าสินค้า
def cart(request):
    cart_items = request.session.get('cart', {})
    total_price = 0
    cart_details = []  # รายละเอียดสินค้าที่จะแสดงในเทมเพลต
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total_price = product.price * quantity
            total_price += item_total_price
            cart_details.append({
                'product': product,
                'quantity': quantity,
                'item_total_price': item_total_price
            })
        except Product.DoesNotExist:
            continue  # หากสินค้าไม่พบในฐานข้อมูล จะข้ามไป
    return render(request, 'cart.html', {'cart_details': cart_details, 'total_price': total_price})


# ฟังก์ชันการค้นหา Outfit
class OutfitSearchView(ListView):
    model = Outfit
    template_name = 'outfit_search.html'
    context_object_name = 'outfits'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Outfit.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__icontains=query)
            )
        return Outfit.objects.all()



# ฟังก์ชันการชำระเงิน
def checkout(request):
    if request.method == "POST":
        # ประมวลผลการชำระเงิน
        process_checkout(request)
        return redirect('checkout_complete')  # เปลี่ยนเส้นทางไปที่หน้า checkout complete
    return render(request, 'checkout.html')


# ฟังก์ชันคืนสินค้า
def return_outfit(request):
    return render(request, 'return.html', {'message': 'Return item form goes here'})


# ฟังก์ชันแสดงรายละเอียดสินค้า
# Mockup data
# Mockup data for the product



def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'rental/product_detail.html', {'product': product})


# ฟังก์ชันแสดงหมวดหมู่สินค้า
def category_list(request):
    categories = [
        {"name": "ชุดเดรส", "image": "https://source.unsplash.com/100x100/?dress"},
        {"name": "เสื้อ", "image": "https://source.unsplash.com/100x100/?shirt"},
        {"name": "กระโปรง", "image": "https://source.unsplash.com/100x100/?skirt"},
        {"name": "กางเกง", "image": "https://source.unsplash.com/100x100/?pants"},
    ]
    return render(request, 'rental/category_list.html', {'categories': categories})


# ฟังก์ชันคำแนะนำการเช่า
def how_to_rent(request):
    return render(request, 'rental/how_to_rent.html')



# ฟังก์ชันบัญชีผู้ใช้
def account(request):
    return render(request, 'rental/account.html')


# ฟังก์ชันการค้นหาสินค้า
def outfit_search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Outfit.objects.filter(name__icontains=query)  # หรือจะใช้ description ด้วยก็ได้

    return render(request, 'rental/outfit_search.html', {
        'results': results,
        'query': query
    })


def product_list(request):
    products = Product.objects.all()  # ดึงสินค้าทั้งหมดจากฐานข้อมูล

    # ฟิลเตอร์ตามหมวดหมู่
    category = request.GET.get('category')
    if category:
        products = products.filter(category_id=category)

    # ฟิลเตอร์ตามคำค้นหา
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)

    return render(request, 'rental/product_list.html', {'products': products})

# ฟังก์ชันแสดงเทรนด์
def trend_list(request):
    trends = Trend.objects.all()
    return render(request, 'rental/trend_list.html', {'trends': trends})
