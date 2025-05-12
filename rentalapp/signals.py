# rentalapp/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Rental
from django.utils import timezone

@receiver(post_save, sender=Order)
def create_rental_when_payment_confirmed(sender, instance, created, **kwargs):
    # ตรวจสอบว่ามีการเปลี่ยนแปลงสถานะการชำระเงินและสถานะเป็น True
    if not created and instance.is_paid and instance.status == 'waiting_for_verification':
        cart_items = instance.cart_items.all()  # สมมติว่าคุณมีการเชื่อม CartItem กับ Order
        for item in cart_items:
            Rental.objects.create(
                user=instance.user,
                product=item.product,
                size=item.size,
                color=item.color,
                rent_days=item.rent_days,
                start_date=timezone.now().date(),
                total_price=item.total_price(),
                is_payment_verified=True,  # ตั้งค่าให้เป็น True เมื่อชำระเงินแล้ว
            )
            # ลดสต็อกสินค้าที่เช่า
            item.product.stock -= item.quantity
            item.product.save()
