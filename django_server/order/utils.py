from decimal import Decimal
from django.core.mail import send_mail
from django.template.loader import render_to_string 

def validate_order(order, option_data, option_ids):
    error_list = []
    pre_order_list = []
    if len(option_ids) != option_data.count():
        raise Exception('some option not exists')
    for option in order:
        option_d = option_data.get(id=option['id'])
        if option['added_quantity'] > option_d.total_quantity:
            pre_order_list.append({"pre_order": option['added_quantity'] - option_d.total_quantity, "id":option['id']})
        if Decimal(option['markdown_price']) != option_d.markdown_price:
            error_list.append({"message": 'markdown_price not match', "id":option['id']})
        if Decimal(option['original_price']) != option_d.original_price:
            error_list.append({"message": 'original_price not match', "id":option['id']})
        if not option_d.availability:
            error_list.append({"message": 'option not availability', "id":option['id']})
    return error_list, pre_order_list

def get_total_price(order, option_data):
    total_price = Decimal(0)
    for option in order:
        option_d = option_data.get(id=option['id'])
        if option_d.markdown_price:
            total_price += option_d.markdown_price * option['added_quantity']
        else:
            total_price += option_d.original_price * option['added_quantity']
    return Decimal(float("{:.2f}".format(total_price)))

def get_delivery_fee(delivery_method):
    if delivery_method == "sf_pay_in_arrive":
        return 0
    elif delivery_method == "sf_pay_in_store":
        return 25
    elif delivery_method == "sf_pay_in_home":
        return 30
    
def send_order_email(to_email ,date, order_refId, user_name, order_url, order):

    html_template = 'order.html'
    html_message = render_to_string(html_template, { 'date': date, "order_refId":order_refId, "user_name": user_name, "order_url": order_url, "order": order })

    send_mail(
        subject="HK Warm Home已收到編號為#{}的訂購訊息 ！".format(order_refId),
        from_email='order@hkwarmhome.com',
        message=html_message,
        recipient_list=[to_email, "hk.warmhome@gmail.com"],
        html_message=html_message
    )

def send_delivery_email(to_email , order_refId, user_name, order_url, order, delivery_id):
    delivery_url = "https://htm.sf-express.com/hk/tc/dynamic_function/waybill/#search/bill-number/" + delivery_id
    html_template = 'delivery_info.html'
    html_message = render_to_string(html_template, { "order_refId":order_refId, "user_name": user_name, "order_url": order_url, "order": order, "delivery_url": delivery_url })

    send_mail(
        subject="你的訂單已在運送-#{} ！".format(order_refId),
        from_email='order@hkwarmhome.com',
        message=html_message,
        recipient_list=[to_email],
        html_message=html_message
    )