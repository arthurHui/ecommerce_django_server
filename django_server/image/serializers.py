from rest_framework import serializers
from image.utils import image_calculator

from image.models import Image, Video

class ImageCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['refId', 'high_resolution', 'low_resolution', 'created','updated','image_type']

    def create(self, validated_data):
        request = self.context.get('request')
        is_webp = request.GET.get('is_webp', False)
        image_type = self.context.get("image_type")
        memory_image = self.context.get("memory_image")
        image = Image.objects.create(image_type=image_type)
        image.high_resolution = image_calculator(memory_image, 2048, 'high', is_webp)
        image.low_resolution = image_calculator(memory_image, 1024, 'low', is_webp)
        image.save()

        return image

class ImageListRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['refId', 'high_resolution', 'low_resolution', 'created','updated','image_type']  

class ImageListRetrieveLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['high_resolution', 'low_resolution']   

class VideoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['refId', 'url', 'created','updated']

    def create(self, validated_data):
        memory_image = self.context.get("memory_image")
        image = Video.objects.create(url=memory_image)
        image.save()

        return image

class VideoListRetrieveLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['url']