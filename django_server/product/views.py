import traceback
from rest_framework import viewsets
from django.db import transaction
from image.models import Image
from product.models import Product, ProductOption, Category, Review
from product import serializers
from rest_framework.response import Response
from rest_framework import status
from utils import custom_paginator
from django.db.models import Avg
from django.core.cache import cache
from django.db import connection

class ProductView(viewsets.ModelViewSet):

    def create(self, request):
        serializer = serializers.ProductCreateUpdateSerializer(data=request.data, context={"request": request})
        try:
            with transaction.atomic():
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request):
        try:
            action = request.GET.get('action', None)
            product_ids = []
            if action == "top3":
                products = Product.objects.raw("""SELECT a.*, b.original_price, b.markdown_price from (
                                                SELECT pp.id, pp.title, pp.availability, MIN(po.id) as m_poid ,SUM(po.sold) as product_option__sold
                                                FROM product_product pp, product_productoption po
                                                WHERE is_deleted=False
                                                AND pp.id = po.product_id
                                                GROUP BY pp.id
                                                ORDER BY product_option__sold DESC
                                                ) as a
                                                LEFT join product_productoption as b
                                                on a.id = b.product_id
                                                AND a.m_poid = b.id
                                                LIMIT 3""")

                # for product in products:
                #     product_ids.append(product.id)
                # images= Image.objects.raw("""SELECT ii.id, ii.high_resolution, ii.low_resolution, pppi.product_id
                #                             from image_image ii, (select *, row_number() over (partition by product_id order by id) as row_num from product_product_product_images) as pppi
                #                             WHERE ii.id = pppi.image_id
                #                             AND pppi.product_id in %s
                #                             AND row_num <= 2""", params=[product_ids])
                serializer = serializers.ProductListRetrieveLiteSerializer(products, many=True)
                results = {"results": serializer.data, " count": 3} 
                return Response(results, status=status.HTTP_200_OK)
            elif action == "in_stock":
                products = Product.objects.filter(product_option__total_quantity__gt=0, is_deleted=False).distinct()
                # images= Image.objects.raw("""SELECT ii.id, ii.high_resolution, ii.low_resolution, pppi.product_id
                #             from image_image ii, (select *, row_number() over (partition by product_id order by id) as row_num from product_product_product_images) as pppi
                #             WHERE ii.id = pppi.image_id
                #             AND pppi.product_id in %s
                #             AND row_num <= 2""", params=[product_ids])
                serializer = serializers.ProductListRetrieveLiteSerializer(products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif action == "all_product_title":
                data = list(Product.objects.filter(is_deleted=False).values_list("title", flat=True))
                return Response(data, status=status.HTTP_200_OK)
            else:
                keyword = request.GET.get('keyword', None)
                page = int(request.GET.get('page', 1))
                psize = int(request.GET.get('psize', 28))
                if keyword:
                    cache_key = 'product_list_{}_{}_{}'.format(keyword, page, psize)
                else:
                    cache_key = 'product_list_{}_{}'.format(page, psize)
                cache_time = 8640000
                data = cache.get(cache_key)
                if not data:
                    filterd_product = self.filter_products(request)
                    product_list, total_page, total_count = custom_paginator(filterd_product, page, psize)
                    serializer = serializers.ProductListRetrieveLiteSerializer(product_list, many=True)
                    results = {"results": serializer.data, "count": total_count}
                    cache.set(cache_key, results, cache_time)
                else:
                    results = data
                return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, title):
        try:
            cache_key = 'retrieve_product_{}'.format(title)
            cache_time = 8640000
            data = cache.get(cache_key)
            if not data:
                product = Product.objects.get(title=title)          
                serializer = serializers.ProductListRetrieveSerializer(product)
                cache.set(cache_key, serializer.data, cache_time)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                cursor = connection.cursor()
                cursor.execute("""select po.id, po.total_quantity 
                               from product_productoption po, product_product pp
                               where po.product_id=pp.id
                               and pp.title=%s""", [title])
                rows = cursor.fetchall()
                for value in data["option"]:
                    for row in rows:
                        if value["id"] == row[0]:
                            value["total_quantity"] = row[1]
                return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def filter_products(self, request):
        keyword = request.GET.get('keyword', None)
        query={
            "is_deleted": False
        }
        if keyword:
            query["title__icontains"] = keyword
        product = Product.objects.filter(**query)
        return product.distinct()

    def sorted_products(self, request, products):
        ordering = None
        if request.GET.get('created', None) is not None:
            ordering = 'ordering_created' if request.GET.get('created') == 'ascending' else '-ordering_created'
        elif request.GET.get('price', None) is not None:
            ordering = 'price' if request.GET.get('price') == 'ascending' else '-price'
        elif request.GET.get('view', None) is not None:
            ordering = 'view' if request.GET.get('view') == 'ascending' else '-view'
        elif request.GET.get('sold', None) is not None:
            ordering = 'sold' if request.GET.get('view') == 'ascending' else '-sold'
        return products.order_by(ordering) if ordering is not None else products
    
class CategoryView(viewsets.ModelViewSet):

    def create(self, request):
        try:
            serializer = serializers.CategoryCreateUpdateSerializer(data=request.data)
            with transaction.atomic():
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request):
        try:
            action = request.GET.get('action', None)
            if action == "product":
                keyword = request.GET.get('keyword', None)
                page = int(request.GET.get('page', 1))
                psize = int(request.GET.get('psize', 28))
                if keyword:
                    cache_key = 'category_action_product_{}_{}_{}'.format(keyword, page, psize)
                else: 
                    cache_key = 'category_action_product_{}_{}'.format(page, psize)
                cache_time = 86400
                data = cache.get(cache_key)
                if not data:
                    filterd_product = self.filter_products(request)
                    product_list, total_page, total_count = custom_paginator(filterd_product, page, psize)
                    serializer = serializers.ProductListRetrieveLiteSerializer(product_list, many=True)
                    results = {"results": serializer.data, "count": total_count} 
                    cache.set(cache_key, results, cache_time)
                else:
                    results = data
                return Response(results, status=status.HTTP_200_OK)
            else:
                cache_key = 'category_list'
                cache_time = 86400
                data = cache.get(cache_key)
                if not data:
                    category = Category.objects.all()
                    serializer = serializers.CategoryListRetrieveSerializer(category, many=True)
                    results = serializer.data
                    cache.set(cache_key, results, cache_time)
                else:
                    results = data
                return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, title):
        try:
            action = request.GET.get('action', None)
            if action == "product":
                cache_key = 'retrieve_category_action_product_{}'.format(title)
                cache_time = 86400
                data = cache.get(cache_key)
                if not data:
                    category = Category.objects.get(title=title)
                    page = int(request.GET.get('page', 1))
                    psize = int(request.GET.get('psize', 28))
                    product_list, total_page, total_count = custom_paginator(category.product_set.all(), page, psize)
                    serializer = serializers.ProductListRetrieveLiteSerializer(product_list, many=True)
                    results = {"results": serializer.data, "count": total_count} 
                    cache.set(cache_key, results, cache_time)
                else:
                    results = data
                return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def filter_products(self, request):
        keyword = request.GET.get('keyword', None)
        query={
            "is_deleted": False
        }
        if keyword:
            query["title__icontains"] = keyword
        product = Product.objects.filter(**query)
        return product.distinct()
        
class ProductReviewView(viewsets.ModelViewSet):
    def create(self, request):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            with transaction.atomic():
                serializer = serializers.ReviewCreateUpdateSerializer(data=request.data, context={'request': request, 'user': user})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request):
        try:
            product_title = request.GET.get("product_title")
            page = int(request.GET.get('page', 1))
            psize = int(request.GET.get('psize', 28))
            product = Product.objects.get(title=product_title)
            review = Review.objects.filter(product_option__product=product)
            total_rate = review.aggregate(Avg('rate'))['rate__avg']
            review_list, total_page, total_count = custom_paginator(review, page, psize)
            serializer = serializers.ReviewListRetrieveSerializer(review_list, many=True)
            results = {"results": serializer.data, "count": total_count, 'total_rate': total_rate} 
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            print(traceback.format_exc())
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
