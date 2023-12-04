from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.ManyToManyField('product.Category')
    availability = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    product_images = models.ManyToManyField('image.Image', related_name='product_images')
    sold = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    video = models.ForeignKey('image.Video', related_name='product_video', on_delete=models.SET_NULL, blank=True, null=True)

    def get_absolute_url(self):
        return "/product/{}".format(self.title)

    class Meta:
        ordering = ["-created"]

class ProductOption(models.Model):
    title = models.CharField(max_length=100)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    markdown_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    availability = models.BooleanField(default=True)
    sold = models.PositiveIntegerField(default=0)
    total_quantity = models.IntegerField(default=0, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    product_option_images = models.ForeignKey('image.Image', related_name='product_option_image', on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey('product.Product', related_name='product_option', on_delete=models.CASCADE, null=True)

class SubProductOption(models.Model):
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    availability = models.BooleanField(default=True)
    total_quantity = models.IntegerField(default=0, blank=True)
    product_option = models.ForeignKey('product.ProductOption', related_name='sub_product_option', on_delete=models.CASCADE)

class Category(models.Model):
    title = models.CharField(max_length=17, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return "/product/{}".format(self.title)

class SoldHistory(models.Model):
    sold = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_option = models.ForeignKey('product.ProductOption', blank=True, null=True, related_name='option_sold_history', on_delete=models.SET_NULL)
    order = models.ForeignKey('order.Order', blank=True, null=True, related_name='order_sold_history', on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created"]

class Review(models.Model):
    product_option = models.ForeignKey('product.ProductOption', related_name='product_option_review', on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    rate = models.IntegerField()
    review_images = models.ManyToManyField('image.Image', related_name='review_images')
    order = models.ForeignKey('order.Order', related_name='order_review', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_hidden = models.BooleanField(default=False)
    class Meta:
        ordering = ["-created"]
        unique_together = ["product_option", "order", "user"]
