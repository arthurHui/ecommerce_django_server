from django.urls import path

from order import views

check_order = views.OrderCheckView.as_view({
    'post': 'create',
})

order_view = views.OrderView.as_view({
    'get': 'list',
    'post': 'create',
})

single_order_view = views.OrderView.as_view({
    'get': 'retrieve',
    'post': 'update',
})

stripe_view = views.CreateStripeCheckoutSessionView.as_view({
    'post': 'create',
})

stripe_webhook_view = views.StripeWebhookView.as_view({
    'post': 'create',
})

order_email_view = views.OrderEmailView.as_view({
    'post': 'create',
})

urlpatterns = [
    path('check', check_order),
    path('order', order_view),
    path('order/<str:refId>', single_order_view),
    path('payment/stripe', stripe_view),
    path("webhooks/stripe", stripe_webhook_view),
    path("email", order_email_view),
]
