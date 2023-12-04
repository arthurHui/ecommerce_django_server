from rest_framework import serializers
from account.serializers import UserListRetrieveSerializer
from order.models import Order
from image.serializers import ImageListRetrieveLiteSerializer, VideoListRetrieveLiteSerializer

from product.models import Category, Product, ProductOption, SubProductOption, Review
from image.models import Image, Video
from django.db.models import Avg

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    product_images = serializers.SerializerMethodField()
    option = serializers.SerializerMethodField()
    product_video = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'category','availability','is_deleted',
                  'product_images','option','sold','created','updated', 'product_video']

    def create(self, validated_data):
        request = self.context.get('request')
        data = request.data
        option_data = data.pop('option')
        category_data = data.pop('category')
        product_images_data = data.pop('product_images')
        product_video_data = data.pop('video', None)
        category = Category.objects.filter(id__in=category_data)
        product_images = Image.objects.filter(refId__in=product_images_data)
        product = Product.objects.create(**validated_data)
        product.category.add(*category)
        if product_video_data:
            product_video = Video.objects.get(refId=product_video_data)
            product.video = product_video
        
        for product_image in product_images:
            product.product_images.add(product_image)
        for option in option_data:
            option_image = option.pop("image", None)
            sub_product_option = option.pop('sub_option', None)
            product_option = ProductOption.objects.create(product=product, **option)
            if option_image:
                product_option.product_option_images = Image.objects.get(refId=option_image)
            product_option.save()
            if sub_product_option:
                for sub_option in sub_product_option:
                    SubProductOption.objects.create(product_option=product_option, **sub_option)
        return product
    
    def get_category(self, obj):
        return CategoryListRetrieveSerializer(obj.category.all(), many=True).data
    
    def get_product_images(self, obj):
        return ImageListRetrieveLiteSerializer(obj.product_images.all(), many=True).data
    
    def get_product_video(self, obj):
        return VideoListRetrieveLiteSerializer(obj.video).data
    
    def get_option(self, obj):
        return ProductOptionListRetrieveSerializer(obj.product_option.all(), many=True).data

class ProductListRetrieveSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    product_images = serializers.SerializerMethodField()
    option = serializers.SerializerMethodField()
    product_video = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'category','availability','is_deleted',
                  'product_images','option', 'product_video']
    
    def get_category(self, obj):
        return CategoryListRetrieveSerializer(obj.category.all(), many=True).data
    
    def get_product_images(self, obj):
        return ImageListRetrieveLiteSerializer(obj.product_images.all(), many=True).data
    
    def get_product_video(self, obj):
        return VideoListRetrieveLiteSerializer(obj.video).data

    def get_option(self, obj):
        return ProductOptionListRetrieveSerializer(obj.product_option.all(), many=True).data 

class ProductListRetrieveLiteSerializer(serializers.ModelSerializer):
    product_images = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    markdown_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title','availability','is_deleted','product_images', 'original_price', 'markdown_price']
    
    def get_product_images(self, obj):
        return ImageListRetrieveLiteSerializer(obj.product_images.all()[0:2], many=True).data

    def get_original_price(self, obj):
        return obj.product_option.first().original_price
    
    def get_markdown_price(self, obj):
        return obj.product_option.first().markdown_price
    
class ProductListRetrieveLiteSQLSerializer(serializers.ModelSerializer):
    product_images = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    markdown_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title','availability','is_deleted','product_images', 'original_price', 'markdown_price']
    
    def get_product_images(self, obj):
        images = self.context['images']
        image_list = []
        for image in images:
            if image.product_id == obj.id:
                image_list.append(image)
        return ImageListRetrieveLiteSerializer(image_list, many=True).data
    
    def get_original_price(self, obj):
        return obj.original_price
    
    def get_markdown_price(self, obj):
        return obj.markdown_price

class ProductOptionListRetrieveSerializer(serializers.ModelSerializer):
    product_option_image = serializers.SerializerMethodField()
    sub_product_option = serializers.SerializerMethodField()

    class Meta:
        model = ProductOption
        fields = ['id', 'title', 'original_price','markdown_price','availability',
                  'total_quantity','created','updated' ,'product_option_image', 'sub_product_option']

    def creare(self, validated_data):
        request = self.context.get('request')
        data = request.data
        option_data = data.pop('option')
        product = Product.objects.create(**data)
        ProductOption.objects.create(product=product, **option_data)
        return product
    
    def get_product_option_image(self, obj):
        return ImageListRetrieveLiteSerializer(obj.product_option_images).data
    
    def get_sub_product_option(self, obj):
        return SubOptionListRetrieveSerializer(obj.sub_product_option.all(), many=True).data

class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']

    def creare(self, validated_data):
        title = validated_data.get('title')
        category = Category.objects.create(title=title)
        return category

class CategoryListRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id','title']

class SubOptionListRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubProductOption
        fields = ['title', 'availability', 'total_quantity']

class ReviewListRetrieveSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=500)
    rate = serializers.IntegerField()
    updated = serializers.DateTimeField()
    review_image = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    product_option_title = serializers.SerializerMethodField()

    def get_review_image(self, obj):
        return ImageListRetrieveLiteSerializer(obj.review_images, many=True).data

    def get_user(self, obj):
        return UserListRetrieveSerializer(obj.user).data
    
    def get_product_option_title(self, obj):
        return obj.product_option.title
    
class ReviewCreateUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=500)
    rate = serializers.IntegerField()
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = self.context.get('user')
        data = request.data
        product_option_id = data.get('product_option_id')
        order_id = data.get('order_id')
        review_images_data = data.get('review_images_data')
        product_option = ProductOption.objects.get(id=product_option_id)
        order = Order.objects.get(refId=order_id)
        review = Review.objects.create(user=user, order=order, product_option=product_option, **validated_data)
        review_images = Image.objects.filter(refId__in=review_images_data)
        for review_image in review_images:
            review.review_images.add(review_image)
        
        return review