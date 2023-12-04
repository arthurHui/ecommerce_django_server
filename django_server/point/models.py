from django.db import models
from django.contrib.auth.models import User
from point.constants import POINT_TYPE_CHOICES

class Point(models.Model):
    unit = models.IntegerField()
    remaining_unit = models.IntegerField()
    type = models.SmallIntegerField(choices=POINT_TYPE_CHOICES)
    expired_date = models.DateTimeField(default='9999-12-31 23:59:59')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created"]