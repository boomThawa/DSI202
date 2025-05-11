from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

# UserProfile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(r'^\+?(\d{1,4})?[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}$')
        ]
    )
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    sizes = models.JSONField()  # ต้องเป็น JSONField เพื่อรองรับชนิด jsonb
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=20, unique=True, blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    slug = models.SlugField(max_length=150, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_available(self):
        return self.status == 'available' and self.stock > 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def is_in_stock(self, quantity):
        """Check if the requested quantity is in stock."""
        return self.stock >= quantity

    def reduce_stock(self, quantity):
        """Reduce stock by a specific quantity."""
        if self.is_in_stock(quantity):
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Not enough stock available.")

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name


# Cart and CartItem Models
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)
    rent_days = models.PositiveIntegerField(default=3)
    start_date = models.DateField()

    def total_price(self):
        return self.product.price * self.quantity * self.rent_days

    def __str__(self):
        return f"{self.product.name} × {self.quantity} ({self.rent_days} days)"



# Rental Model

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
    rent_days = models.PositiveIntegerField()
    start_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_payment_verified = models.BooleanField(default=False)  # สถานะการชำระเงินที่ Admin ยืนยัน
    payment_verified_date = models.DateTimeField(null=True, blank=True) # วันที่ Admin ยืนยันการชำระเงิน

    def __str__(self):
        return f"Rental #{self.id} by {self.user.username}"

# Trend Model
class Trend(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='trends/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
from django.db import models
from .models import Category

class Outfit(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    size = models.CharField(max_length=20)
    image = models.ImageField(upload_to='outfits/')
    description = models.TextField()

    def __str__(self):
        return self.name




from django.db import models
from django.contrib.auth.models import User

class Checkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rent_days = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Checkout {self.id} - User: {self.user.username}"



class Return(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
    ]

    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='returns')
    status = models.CharField(max_length=13, choices=STATUS_CHOICES, default='pending')
    review = models.TextField(blank=True, help_text="Provide feedback or reason for return.")
    created_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=128)  # ตรวจสอบว่ามีการประกาศฟิลด์นี้

    def __str__(self):
        return f"Return for Order #{self.order.id}"


# rental/models.py
from django.db import models
from django.contrib.auth.models import User
import random
import string

# Define Order model first
def generate_order_id():
    """ Create a random order_id starting with # """
    return '#' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    sub_district = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False) # สำหรับที่อยู่เริ่มต้น

    def __str__(self):
        return f"{self.name} - {self.address_line1}, {self.district}, {self.province}"

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    order_id = models.IntegerField(unique=True, null=True, blank=True)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            last_order = Order.objects.order_by('-order_id').first()
            self.order_id = (last_order.order_id + 1) if last_order and last_order.order_id is not None else 1
        super().save(*args, **kwargs)

# Now define OrderItem model, after the Order model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)
    rent_days = models.PositiveIntegerField(default=3)
    start_date = models.DateField()

    def total_price(self):
        return self.product.price * self.quantity * self.rent_days

    def __str__(self):
        return f"{self.product.name} × {self.quantity} ({self.rent_days} days)"
