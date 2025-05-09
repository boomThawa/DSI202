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
    sizes = models.JSONField(default=list, blank=True, help_text="Available sizes for the product.")
    
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
    sizes = models.JSONField(default=list, blank=True, help_text="Available sizes for the product.")
    colors = models.JSONField(null=True, blank=True)  # เพิ่มฟิลด์ colors
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


# Order Model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


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
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    rent_days = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)  # Confirmed rental or not

    def __str__(self):
        return f"Checkout #{self.id} - {self.product.name} by {self.user.username}"
       




from django.db import models
from django.contrib.auth.models import User

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