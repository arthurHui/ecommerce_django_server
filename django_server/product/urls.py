from django.urls import path

from product import views

product_view = views.ProductView.as_view({
    'get': 'list',
    'post': 'create',
})

retrieve_product = views.ProductView.as_view({
    'get': 'retrieve',
})

category_view = views.CategoryView.as_view({
    'get': 'list',
    'post': 'create',
})

retrieve_category = views.CategoryView.as_view({
    'get': 'retrieve',
})

review_view = views.ProductReviewView.as_view({
    'get': 'list',
    'post': 'create',
})

urlpatterns = [
    path('product', product_view),
    path('product/<str:title>', retrieve_product),
    path('category', category_view),
    path('category/<str:title>', retrieve_category),
    path('review', review_view),
]
