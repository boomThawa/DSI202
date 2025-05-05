# model.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r'^\+?(\d{1,4})?[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}$')])
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'rentalapp'

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # ตรวจสอบว่า slug ซ้ำหรือไม่
        existing_slug = Product.objects.filter(slug=self.slug).aggregate(Max('id'))['id__max']
        if existing_slug:
            self.slug = f"{self.slug}-{existing_slug + 1}"
        if self.stock == 0:
            self.status = 'out_of_stock'
        elif self.status != 'discontinued':
            self.status = 'available'
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class Outfit(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    size = models.CharField(max_length=20)
    image = models.ImageField(upload_to='outfits/')
    description = models.TextField()

    def clean(self):
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    outfits = models.ManyToManyField(Outfit, related_name='orders')
    total_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class Return(models.Model):
    RETURN_METHOD_CHOICES = [
        ('store', 'คืนที่ร้าน'),
        ('pickup', 'รับที่บ้าน'),
    ]

   
    RETURN_STATUS_CHOICES = [
        ('not_requested', 'ยังไม่ร้องขอ'),
        ('pending', 'กำลังรออนุมัติ'),
        ('approved', 'อนุมัติแล้ว'),
        ('rejected', 'ปฏิเสธแล้ว'),
    ]
    return_status = models.CharField(
        max_length=20,
        choices=RETURN_STATUS_CHOICES,
        default='not_requested'
    )
    return_date = models.DateTimeField(null=True, blank=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    method = models.CharField(max_length=100, choices=RETURN_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=RETURN_STATUS_CHOICES, default='pending')
    review = models.TextField(blank=True, help_text="Please provide your feedback or reason for return.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return for Order #{self.order.id}"


class Trend(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='trends/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class OrderOutfit(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=20)

    class Meta:
        unique_together = ('order', 'outfit')

    def __str__(self):
        return f"{self.quantity} of {self.outfit.name} in size {self.size}"

from django.db import models
from django.contrib.auth.models import User
from rentalapp.models import Product

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
    quantity = models.PositiveIntegerField(default=1)
    rent_days = models.PositiveIntegerField(default=3)  # กำหนดค่าเริ่มต้น 3 วัน

    def total_price(self):
        return self.product.price * self.quantity * self.rent_days

    def __str__(self):
        return f"{self.product.name} × {self.quantity} ({self.rent_days} days)"

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rental_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    returned = models.BooleanField(default=False)
    return_date = models.DateTimeField(null=True, blank=True)

class RentalItem(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rent_days = models.PositiveIntegerField()
    price_per_day = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def total(self):
        return self.rent_days * self.price_per_day
