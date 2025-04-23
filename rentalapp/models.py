from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'rentalapp'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField()
    image = models.ImageField(upload_to='product_images/')
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Outfit(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    size = models.CharField(max_length=20)
    image = models.ImageField(upload_to='outfits/')
    description = models.TextField()

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    outfits = models.ManyToManyField(Outfit)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Return(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=100, choices=[('store', 'คืนที่ร้าน'), ('pickup', 'รับที่บ้าน')])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Trend(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='trends/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# You can also keep your search view separately in the appropriate views file, 
# but for models.py, this is enough.
