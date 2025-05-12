#/Users/thawaphorn/Desktop/dsi202-final/rental/rentalapp/urls.py
from django.urls import path, include  # <<< ต้องมี include ด้วย
from . import views
from .views import ProfileView, view_cart


urlpatterns = [
    # หน้าหลัก
    path('', views.home, name='home'),

    # ฟีเจอร์ผู้ใช้
    path('profile/', ProfileView.as_view(), name='profile'),  # ใช้ CBV สำหรับ Profile
    path('wishlist/', views.wishlist, name='wishlist'),  # ตรวจสอบว่าฟังก์ชันนี้มีอยู่
    path('return/', views.return_outfit, name='return_outfit'),
    path('cart/', views.view_cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),

    path('rent_now/<int:product_id>/', views.rent_now, name='rent_now'),
    path('remove-cart-item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('update_rent_days/<int:item_id>/', views.update_rent_days, name='update_rent_days'),
    path('checkout/', views.checkout, name='checkout'),  # เปลี่ยนตรงนี้
    path('invoice/<int:rental_id>/', views.invoice, name='invoice'),
    path('process-payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),



    path('thank-you/', views.thank_you, name='thank_you'),  # เพิ่ม URL สำหรับ thank_you
    path('history/', views.rental_history, name='rental_history'),

    # สินค้า
    path('rental/<int:rental_id>/return/', views.return_request, name='return_request'),

    # สินค้า
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/', views.category_list, name='category_list'),

    # คอนเทนต์ + แฟชั่น
    path('trends/', views.trend_list, name='trend_list'),

    # การเข้าสู่ระบบและออกจากระบบ
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # การจัดการการคืนสินค้า
    path('admin/returns/', views.manage_returns, name='manage_returns'),
    path('admin/returns/<int:rental_id>/approve/', views.approve_return, name='approve_return'),
    path('admin/returns/<int:rental_id>/reject/', views.reject_return, name='reject_return'),
]