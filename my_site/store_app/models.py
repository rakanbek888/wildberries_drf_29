from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    STATUS_CHOICES = (
        ('gold', 'gold'),
        ('silver', 'silver'),
        ('bronze', 'bronze'),
        ('simple', 'simple'),
    )
    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(16), MaxValueValidator(70)],
        null=True,
        blank=True
    )
    phone_number = PhoneNumberField(blank=True, null=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='simple')
    date_register = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    category_name = models.CharField(max_length=32, unique=True)
    category_image = models.ImageField(upload_to='photo_category/')

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    subcategory_name = models.CharField(max_length=32)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        unique_together = ('subcategory_name', 'category')

    def __str__(self):
        return self.subcategory_name


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    description = models.TextField()
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    product_type = models.BooleanField(default=True)
    article = models.PositiveIntegerField(unique=True)
    video = models.FileField(upload_to='product_videos/', null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    def get_avg_rating(self):
        ratings = self.product_review.exclude(star__isnull=True)
        if ratings.exists():
            return round(sum(i.star for i in ratings) / ratings.count(), 2)
        return 0

    def get_count_people(self):
        return self.product_review.count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    product_image = models.ImageField(upload_to='image_product/')

    def __str__(self):
        return self.product.product_name


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_review')
    star = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1)
    text = models.TextField(default="")
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}'

    def get_total_price(self):
        return sum([i.get_total_price() for i in self.items.all()])


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"

    def get_total_price(self):
        return self.quantity * self.product.price