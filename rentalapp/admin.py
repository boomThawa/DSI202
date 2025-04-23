#admin.py

from django.contrib import admin
from .models import Outfit, Category, Order, Return

admin.site.register(Outfit)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Return)

from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')  # ข้อมูลที่แสดงในหน้า Admin
    search_fields = ('name', 'description')  # สามารถค้นหาด้วยชื่อหรือคำอธิบายสินค้า

admin.site.register(Product, ProductAdmin)

