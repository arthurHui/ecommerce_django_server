from django.db import models

from django.db import models
from django.contrib.auth.models import User

class UserDetail(models.Model):
    birthday = models.CharField(null=True, blank=True, max_length=20)
    phone = models.CharField(null=True, blank=True, max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_allow_promotion = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)