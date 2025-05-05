from django.contrib import admin
from django.contrib.auth.models import User
from .models import Category, Product, Outfit, Order, Return, Trend, UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# 1. Register Category, Product, Outfit, Order, Return, Trend
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

# 2. เพิ่มการจัดการ UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'address']

# 3. สร้าง Inline สำหรับ UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

# 4. สร้าง Custom User Admin
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]

# 5. Unregister และ Register ใหม่สำหรับ User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
