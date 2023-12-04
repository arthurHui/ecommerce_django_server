from django.db import transaction
from rest_framework import viewsets
from image.models import Image
from image import serializers
from rest_framework.response import Response
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import traceback

class ImageView(viewsets.ModelViewSet):

    def create(self, request):
        try:
            with transaction.atomic():
                files = request.FILES
                images = files.getlist('images')
                file = files.getlist('file')
                res = []
                for file_image in images:
                    image_type = file_image.name.split('.')[-1].lower()
                    memory_image = SimpleUploadedFile(file_image.name,file_image.read(),file_image.content_type)
                    serializer = serializers.ImageCreateUpdateSerializer(data=request.data, context={"image_type": image_type, "memory_image":memory_image, "request": request})
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        res.append(serializer.data)
                for file_image in file:
                    image_type = file_image.name.split('.')[-1].lower()
                    memory_image = SimpleUploadedFile(file_image.name,file_image.read(),file_image.content_type)
                    serializer = serializers.ImageCreateUpdateSerializer(data=request.data, context={"image_type": image_type, "memory_image":memory_image, "request": request})
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        res.append(serializer.data)
                return Response(data=res, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class VideoView(viewsets.ModelViewSet):

    def create(self, request):
        try:
            with transaction.atomic():
                files = request.FILES
                videos = files.getlist('videos')
                res = []
                for video in videos:
                    memory_image = SimpleUploadedFile(video.name,video.read(),video.content_type)
                    serializer = serializers.VideoCreateUpdateSerializer(data=request.data, context={"memory_image":memory_image})
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                        res.append(serializer.data)
                return Response(data=res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)