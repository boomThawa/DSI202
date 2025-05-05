from django.urls import path
from . import views
from .views import ProfileView,cart

urlpatterns = [
    # หน้าหลัก
    path('', views.home, name='home'),

    # ฟีเจอร์ผู้ใช้
    path('profile/', ProfileView.as_view(), name='profile'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('return/', views.return_outfit, name='return_outfit'),
    path('account/', views.account, name='account'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('rent_now/<int:product_id>/', views.rent_now, name='rent_now'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_rent_days/<int:item_id>/', views.update_rent_days, name='update_rent_days'),
    path('invoice/<int:rental_id>/', views.invoice, name='invoice'),
    path('rental/history/', views.rental_history, name='rental_history'),
    path('rental/<int:rental_id>/return/', views.return_request, name='return_request'),

    # สินค้า
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/', views.category_list, name='category_list'),

    # คอนเทนต์ + แฟชั่น
    path('trends/', views.trend_list, name='trend_list'),
    path('outfit-search/', views.outfit_search, name='outfit_search'),
    path('outfit/<int:pk>/', views.OutfitDetailView.as_view(), name='outfit_detail'),

    # วิธีการเช่า
    path('how-to-rent/', views.how_to_rent, name='how_to_rent'),

    # การเข้าสู่ระบบและออกจากระบบ
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # การจัดการการคืนสินค้า
    path('admin/returns/', views.manage_returns, name='manage_returns'),
    path('admin/returns/<int:rental_id>/approve/', views.approve_return, name='approve_return'),
    path('admin/returns/<int:rental_id>/reject/', views.reject_return, name='reject_return'),
]
