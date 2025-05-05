from django.contrib import admin
from .models import Category, Product, Outfit, Order, Return, Trend

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_featured')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')

@admin.register(Outfit)
class OutfitAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'size')
    list_filter = ('category', 'size')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'is_paid', 'created_at')
    list_filter = ('is_paid',)
    search_fields = ('user__username',)

@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'created_at')
    list_filter = ('method',)

@admin.register(Trend)
class TrendAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

from django.contrib.auth.decorators import login_required
@login_required
def profile(request):
    return render(request, 'rental/profile.html')