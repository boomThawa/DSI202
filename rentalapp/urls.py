from django.urls import path
from . import views

urlpatterns = [
    # หน้าหลัก
    path('', views.home, name='home'),

    # ฟีเจอร์ผู้ใช้
    path('wishlist/', views.wishlist, name='wishlist'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('return/', views.return_outfit, name='return_outfit'),
    path('account/', views.account, name='account'),

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
]
