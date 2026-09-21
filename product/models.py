from django.db import models
from home.models import User
from home.utils import BaseModel


class Product(BaseModel):
    product_id = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=250, default="Unknown")
    category = models.CharField(max_length=50, default="Women")
    sub_category = models.CharField(max_length=100, null=True, blank=True)
    max_retail_price = models.IntegerField(default=500)
    colour = models.CharField(max_length=50, null=True, blank=True)
    brand = models.CharField(max_length=50, null=True, blank=True)
    product_image = models.FileField(upload_to="products/", null=True, blank=True)
    product_description = models.CharField(max_length=500, null=True, blank=True)
    rating_count = models.IntegerField(default=0)
    average_rating = models.IntegerField(default=0)

    def __str__(self):
        return self.product_name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.max_retail_price


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.product.max_retail_price