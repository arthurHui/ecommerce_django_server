from django.urls import path

from image import views

image_view = views.ImageView.as_view({
    'get': 'list',
    'post': 'create',
})

video_view = views.VideoView.as_view({
    'get': 'list',
    'post': 'create',
})

urlpatterns = [
    path('image', image_view),
    path('video', video_view),
]
