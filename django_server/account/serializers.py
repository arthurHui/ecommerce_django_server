from rest_framework import serializers
from django.contrib.auth.models import User
from account.models import UserDetail
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from django.db.models import Sum

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    token = serializers.SerializerMethodField()
    birthday = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id','username', 'password', 'email', 'first_name', 'last_name', 'token', 'birthday', 'phone']

    def create(self, validated_data):
        request = self.context.get("request")
        birthday = request.data.get('birthday')
        user = User.objects.create(**validated_data)
        UserDetail.objects.create(birthday=birthday,user=user)
        Token.objects.create(user=user)
        
        return user
    
    def get_token(self, obj):
        return Token.objects.get(user=obj).key
    
    def get_birthday(self, obj):
        return obj.userdetail.birthday
    
    def get_phone(self, obj):
        return obj.userdetail.phone
    
class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    birthday = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    password = serializers.CharField(required=False, validators=[validate_password])
    old_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(
            required=False,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    
    class Meta:
        model = User
        fields = ['id','username', 'password', 'old_password', 'email', 'first_name', 'last_name', 'birthday', 'phone']

    def update(self, instance, validated_data):
        if validated_data.get('password',None) and validated_data.get('old_password',None) != instance.password:
            raise Exception('old password not match')
        request = self.context.get("request")
        instance.email = validated_data.get('email',instance.email)
        instance.username = validated_data.get('username',instance.username)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.password = validated_data.get('password',instance.password)
        instance.email = validated_data.get('email',instance.email)
        user_detail = instance.userdetail
        user_detail.birthday = request.data.get('birthday',user_detail.birthday)
        user_detail.phone = request.data.get('phone',user_detail.phone)
        user_detail.save()
        instance.save()

        return instance
    
    def get_birthday(self, obj):
        return obj.userdetail.birthday

    def get_phone(self, obj):
        return obj.userdetail.phone
       
class UserListRetrieveSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    birthday = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id','username', 'email', 'first_name', 'last_name', 'token', 'birthday', 'phone']
    
    def get_token(self, obj):
        try:
            return Token.objects.get(user=obj).key
        except:
            return None

    def get_birthday(self, obj):
        return obj.userdetail.birthday
    
    def get_phone(self, obj):
        return obj.userdetail.phone
