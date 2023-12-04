from django.core.paginator import Paginator

def custom_paginator(obj, page, page_size):
    paginator = Paginator(obj, page_size)
    return paginator.page(page).object_list, paginator.num_pages, paginator.count