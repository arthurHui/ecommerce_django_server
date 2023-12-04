import uuid
from django.db import models
from django.contrib.auth.models import User
import datetime

from order.constants import ORDER_STATUS_CHOICES, PAYMENT_STATUS_CHOICES, DELIVERY_STATUS_CHOICES, PAYMENT_METHOD_CHOICES

class Order(models.Model):
    refId = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_id = models.CharField(default=datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'), max_length=30)
    data = models.TextField()
    status = models.PositiveSmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1)
    payment_status = models.PositiveSmallIntegerField(choices=PAYMENT_STATUS_CHOICES, default=1)
    delivery_status = models.PositiveSmallIntegerField(choices=DELIVERY_STATUS_CHOICES, default=1)
    remarks = models.CharField(default='', blank=True, max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    payment_image = models.ManyToManyField('image.Image', related_name='order_payment_image')
    payment_remark = models.CharField(default='', blank=True, max_length=500)
    payment_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]

class OrderAdditionalDetail(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    stripe_id = models.CharField(null=True, blank=True, max_length=100)

# class PaymentHistory(models.Model):
#     payment_id = models.CharField(max_length=100)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     order = models.ForeignKey(Order,on_delete=models.CASCADE)
#     status = models.PositiveSmallIntegerField(choices=PAYMENT_STATUS_CHOICES)
#     method = models.PositiveSmallIntegerField(choices=PAYMENT_METHOD_CHOICES)
#     amount = models.DecimalField(max_digits=10, decimal_places = 2)
#     service_fee = models.DecimalField(max_digits=10, decimal_places = 6)
#     data = models.TextField() 