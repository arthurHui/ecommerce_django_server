import traceback
from rest_framework import viewsets
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from account import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.cache import cache

class userView(viewsets.ModelViewSet):

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = serializers.UserCreateSerializer(data=request.data, context={"request": request})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            error = {}
            for key, value in e.get_full_details().items():
                error[key] = value[0]["code"]
            print(traceback.format_exc())
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, id, *args, **kwargs):
        try:
            with transaction.atomic():
                user = User.objects.get(id=id)
                serializer = serializers.UserUpdateSerializer(user, data=request.data, context={"request": request})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class userLoginView(viewsets.ModelViewSet):

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            if user.is_authenticated:
                serializer = serializers.UserListRetrieveSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                email = request.data.get('email')
                password = request.data.get('password')
                user = User.objects.get(email=email, password=password)
                Token.objects.get_or_create(user = user)
                serializer = serializers.UserListRetrieveSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, id, *args, **kwargs):
        try:
            user = request.user
            if user.is_authenticated:
                user = User.objects.get(id=id)
                token = Token.objects.get(user=user)
                token.delete()
                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class systemView(viewsets.ModelViewSet):

    def execute(self, request):
        try:
            action = request.GET.get("action", None)
            if action == "clear_cache":
                cache.clear()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)