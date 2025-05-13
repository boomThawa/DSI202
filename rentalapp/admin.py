from django.contrib import admin
from django.contrib.auth.models import User
from .models import Category, Product, Outfit, Order, Return, Trend, UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_featured', 'stock', 'status')
    list_filter = ('category', 'is_featured', 'status')
    search_fields = ('^name', 'description')
    list_editable = ('is_featured', 'stock', 'status')

# Outfit Admin
@admin.register(Outfit)
class OutfitAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'size')
    list_filter = ('category', 'size')
    search_fields = ('^name', 'description')

# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'

# Return Admin
@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'status', 'created_at')
    list_filter = ('method', 'status','created_at')
    search_fields = ('order__id',)

# Trend Admin
@admin.register(Trend)
class TrendAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    date_hierarchy = 'created_at'

# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('^user__username', 'phone_number')

# Inline for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profiles'

# Custom User Admin
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]

from django.contrib import admin
from .models import Product, Category, Rental

from django.contrib import admin
from .models import Product, Category, Rental

class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'start_date', 'total_price', 'is_payment_verified', 'payment_verified_date')
    list_editable = ('is_payment_verified',) # ให้ Admin แก้ไข is_payment_verified ได้โดยตรง
    readonly_fields = ('payment_verified_date',) # แสดงวันที่ยืนยัน แต่แก้ไขไม่ได้

    def save_model(self, request, obj, form, change):
        if change and obj.is_payment_verified and not obj.payment_verified_date:
            obj.payment_verified_date = timezone.now()
        super().save_model(request, obj, form, change)

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_pending_payments(request):
    pending_orders = Order.objects.filter(status='pending_confirmation')
    return render(request, 'admin/pending_payments.html', {'pending_orders': pending_orders})

@staff_member_required
def admin_approve_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'pending_confirmation':
        order.status = 'paid'
        order.save()
        messages.success(request, f"อนุมัติการชำระเงินสำหรับออเดอร์ #{order.id} แล้ว")
        # อาจมีการส่งอีเมลแจ้งเตือนผู้ใช้ที่นี่
    return redirect

# Unregister and Re-register User with CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)