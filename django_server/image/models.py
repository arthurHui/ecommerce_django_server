import datetime
import uuid
from django.db import models

def get_upload_high_resolution_path(instance, filename):
    # r_filename = random.randint(100000000, 999999999)
    return "high/%s_%s.%s" % (uuid.uuid4(), datetime.datetime.now().timestamp()*1000, filename.split('.')[-1].lower())

def get_upload_low_resolution_path(instance, filename):
    # r_filename = random.randint(100000000, 999999999)
    return "low/%s_%s.%s" % (uuid.uuid4(), datetime.datetime.now().timestamp()*1000, filename.split('.')[-1].lower())

class Image(models.Model):
    refId = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    high_resolution = models.ImageField(upload_to=get_upload_high_resolution_path, null=True, blank=True, default=None)
    low_resolution = models.ImageField(upload_to=get_upload_low_resolution_path, null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image_type = models.CharField(max_length=20, blank=True)

class Video(models.Model):
    refId = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    url = models.ImageField(upload_to=get_upload_high_resolution_path, null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)