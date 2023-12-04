from django.urls import path

from account import views

user_view = views.userView.as_view({
    'post': 'create',
})

user_update = views.userView.as_view({
    'post': 'update',
})

user_login = views.userLoginView.as_view({
    'post': 'create',
})

user_logout = views.userLoginView.as_view({
    'post': 'retrieve',
})

system = views.systemView.as_view({
    'post': 'execute',
})

urlpatterns = [
    path('user', user_view),
    path('user/<int:id>', user_update),
    path('login', user_login),
    path('login/<int:id>', user_logout),
    path('system', system),
]
