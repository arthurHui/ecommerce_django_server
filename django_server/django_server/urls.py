from django.contrib import admin
from django.urls import include, path
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap

from product.models import Category, Product

product_dict = {
    "queryset": Product.objects.all(),
    "date_field": "updated",
}

category_dict = {
    "queryset": Category.objects.all(),
    "date_field": "updated",
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('product/', include('product.urls')),
    path('image/', include('image.urls')),
    path('auth/', include('account.urls')),
    path('order/', include('order.urls')),
        path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {
            "product": GenericSitemap(product_dict, priority=0.6),
            "category": GenericSitemap(category_dict, priority=0.6)
            }},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
