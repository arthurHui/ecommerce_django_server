import datetime
from rest_framework import serializers
import json
from constants import WEBSITE_URL
from image.serializers import ImageListRetrieveLiteSerializer
from image.models import Image
from order.utils import get_total_price, get_delivery_fee, send_order_email
from product.models import SoldHistory
from order.models import Order, OrderAdditionalDetail
from decimal import Decimal

class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    data = serializers.CharField(required=False)
    payment_image = serializers.SerializerMethodField()
    payment_date = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = ['refId','data', 'status', 'payment_status', 'delivery_status', 'remarks', 
                  'created', 'payment_image', 'payment_remark', 'payment_date']

    def create(self, validated_data):
        request = self.context.get("request")
        option_data = self.context.get("option_data")
        data = request.data
        order_data = request.data.get('order')
        remarks = request.data.get('remarks')
        total_price = request.data.get('total_price')
        is_to_member = request.data.get('is_to_member')
        user = request.user

        validated_total_price = get_total_price(order_data, option_data)
        order = Order.objects.create(data=json.dumps(data),remarks=remarks)
        total_price = Decimal(float("{:.2f}".format(total_price)))
        if user.is_authenticated:
            order.user = user
            order.save()
            validated_total_price = Decimal(float("{:.2f}".format(validated_total_price * Decimal(0.95))))
        if total_price != validated_total_price:
            raise Exception('total price not match, total_price: {}, validated_total_price: {}'.format(total_price, validated_total_price))
        for option in order_data:
            option_d = option_data.get(id=option['id'])
            option_d.sold += option['added_quantity']
            if option_d.total_quantity >= option['added_quantity']:
                option_d.total_quantity -= option['added_quantity']
            else:
                option['added_quantity'] -= option_d.total_quantity
                option["pre_order"] = option['added_quantity']
            option_d.save()
            sub_total_price = option['added_quantity'] * Decimal(option.get('markdown_price',option['original_price']))
            SoldHistory.objects.create(sold=option['added_quantity'],total_price=sub_total_price,product_option=option_d,order=order)
        data['order'] = order_data
        order.data = json.dumps(data)
        order.save()
        OrderAdditionalDetail.objects.create(order=order)
        send_order_email(request.data['email'], datetime.datetime.now().strftime('%m/%d/%Y'), order.order_id, request.data['customer_name'], WEBSITE_URL+"/order"+"/{}".format(order.refId), order_data)
        return order
    
    def update(self, instance, validated_data):
        request = self.context.get("request")

        payment_image = Image.objects.filter(refId__in=request.data.get("payment_image"))

        instance.payment_image.add(*payment_image)
        instance.payment_date = datetime.datetime.fromtimestamp(int(validated_data.get("payment_date")))
        instance.payment_remark = validated_data.get("payment_remark")
        instance.save()

        return instance
    
    def get_payment_image(self, obj):
        return ImageListRetrieveLiteSerializer(obj.payment_image.all(), many=True).data
    
class OrderListRetrieveSerializer(serializers.ModelSerializer):
    payment_image = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['refId','data', 'status', 'payment_status', 'delivery_status', 'remarks', 
                  'created', 'order_id', 'user', 'payment_image', 'payment_remark', 'payment_date']
    
    def get_payment_image(self, obj):
        return ImageListRetrieveLiteSerializer(obj.payment_image.all(), many=True).data
        
    def get_user(self, obj):
            try:
                return obj.user.id
            except Exception as e:
                return None


class OrderListRetrieveLiteSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['refId', 'total_price', 'status', 'payment_status', 'delivery_status', 'created']

    def get_total_price(self, obj):
        data = json.loads(obj.data)
        return data.get('total_price')
