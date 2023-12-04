import json
from rest_framework import viewsets
from django.db import transaction
from constants import WEBSITE_URL
from order import serializers
from order.utils import validate_order, get_delivery_fee, send_delivery_email
from product.models import ProductOption
from order.models import Order, OrderAdditionalDetail
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
import traceback
import stripe
from django.conf import settings
import base64
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from utils import custom_paginator

stripe.api_key = settings.STRIPE_SECRET_KEY

class OrderCheckView(viewsets.ModelViewSet):

    def create(self, request):
        try:
            order = request.data.get('order')
            option_ids = [i['id'] for i in order]
            option_data = ProductOption.objects.filter(id__in=option_ids)
            error_list, pre_order_list = validate_order(order, option_data, option_ids)
            return Response(data={"error_list":error_list, "pre_order_list":pre_order_list}, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class OrderView(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            if user.is_authenticated:
                action = request.GET.get('action')
                page = int(request.GET.get('page', 1))
                psize = int(request.GET.get('psize', 28))
                orders = Order.objects.filter(user=user).order_by('-created')
                order_list, total_page, total_count = custom_paginator(orders, page, psize)
                if action == "lite":
                    serializer = serializers.OrderListRetrieveLiteSerializer(order_list, many=True)
                else:
                    serializer = serializers.OrderListRetrieveSerializer(order_list, many=True)
                results = {"results": serializer.data, "count": total_count}
                return Response(results, status=status.HTTP_200_OK)
            else:
                raise Exception("not a user")
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, refId, *args, **kwargs):
        try:
            action = request.GET.get('action')
            order = Order.objects.get(refId=refId)
            if action == "lite":
                serializer = serializers.OrderListRetrieveLiteSerializer(order)
            else:
                serializer = serializers.OrderListRetrieveSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        try:
            with transaction.atomic():
                order = request.data.get('order')
                option_ids = [i['id'] for i in order]
                option_data = ProductOption.objects.filter(id__in=option_ids)
                error_list, pre_order_list = validate_order(order, option_data, option_ids)
                if len(error_list) > 0:
                    return Response(data=error_list, status=status.HTTP_400_BAD_REQUEST)
                serializer = serializers.OrderCreateUpdateSerializer(data=request.data, context={"request": request, "option_data":option_data})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, refId,*args, **kwargs):
        try:
            order = Order.objects.get(refId=refId)
            with transaction.atomic():
                serializer = serializers.OrderCreateUpdateSerializer(order, data=request.data, context={"request": request})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class CreateStripeCheckoutSessionView(viewsets.ModelViewSet):
    """
    Create a checkout session and redirect the user to Stripe's checkout page
    """
    def create(self, request):
        try:
            action = request.GET.get('action')
            order = request.data.get('order')
            base_url = request.data.get('url')
            ref_id = request.data.get('refId')
            is_user = request.data.get('is_user')
            payment_method = request.data.get('payment_method')
            line_items = []
            if action == "direct_payment":
                line_items.append({
                    "price_data": {
                        "currency": "hkd",
                        "unit_amount": int(float(order['price'])*100),
                        "product_data": {
                            "name": order['product_title'],
                        },
                    },
                    "quantity": 1,
                })
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=["card","alipay","wechat_pay"],
                    payment_method_options={
                        "wechat_pay":{
                            "client": "web"
                        }
                    },
                    line_items=line_items,
                    mode="payment",
                    success_url="{}?success=true".format(base_url),
                    cancel_url="{}?canceled=true".format(base_url),
                )
                return Response({"url": checkout_session.url}, status=status.HTTP_200_OK)
            else:
                for order_data in order['order']:
                    if is_user:
                        unit_amount = int(float(order_data.get('markdown_price',order_data['original_price']))*0.95*100)
                    else:
                        unit_amount = int(float(order_data.get('markdown_price',order_data['original_price']))*100)
                    line_items.append({
                        "price_data": {
                                "currency": "hkd",
                                "unit_amount": unit_amount,
                                "product_data": {
                                    "name": order_data['product_title'],
                                    "images": [order_data['image']],
                                },
                            },
                        "quantity": order_data['added_quantity'],
                    })
                if order["delivery_fee"] is not None and order["delivery_fee"] > 0:
                    line_items.append({
                        "price_data": {
                            "currency": "hkd",
                            "unit_amount": order["delivery_fee"] * 100,
                            "product_data": {
                                "name": "運費"
                            },
                        },
                        "quantity": 1,
                    })
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=[payment_method],
                    line_items=line_items,
                    mode="payment",
                    success_url="{}?success=true&oi={}".format(base_url, base64.b64encode(ref_id.encode('utf-8')).decode('utf-8')),
                    cancel_url="{}?canceled=true".format(base_url), 
                )
                orderM = Order.objects.get(refId=ref_id)
                order_detail = orderM.orderadditionaldetail
                order_detail.stripe_id = checkout_session.id
                order_detail.save()
                return Response({"url": checkout_session.url}, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(viewsets.ModelViewSet):
    """
    Stripe webhook view to handle checkout session completed event.
    """

    def create(self, request, format=None):
        try:
            payload = request.body
            endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
            sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
            event = None
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            print('event',event)
            if event["type"] == "checkout.session.completed":
                try:
                    order_detail = OrderAdditionalDetail.objects.get(stripe_id=event['data']['object']['id'])
                    order = order_detail.order
                    order.payment_status = 2
                    order.save()
                except Exception as e:
                    print(str(e))
        # Can handle other events here.
        except ValueError as e:
            # Invalid payload
            print("error", str(e)) 
            return Response(status=200)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print("error", str(e))
            return Response(status=200)
        except Exception as e:
            return Response(status=200)
        
        return Response(status=200)

class OrderEmailView(viewsets.ModelViewSet):

    def create(self, request):
        try:
            action = request.GET.get('action')
            if action == "delivery":
                to_email = request.data.get('to_email')
                order_refId = request.data.get('order_refId')
                delivery_id = request.data.get('delivery_id')
                order_obj = Order.objects.get(refId=order_refId)
                order_obj_json = json.loads(order_obj.data)
                order = order_obj_json["order"]
                order_url = WEBSITE_URL+"/order"+"/{}".format(order_obj.refId)
                user_name = order_obj_json["customer_name"]
                
                send_delivery_email(to_email, order_obj.order_id, user_name, order_url, order, delivery_id)
            return Response(status=200)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
