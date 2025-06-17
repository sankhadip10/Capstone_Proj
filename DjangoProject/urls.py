"""
URL configuration for DjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from .views import say_hello,say_hello_with_name
# from .views import users,get_or_update_or_delete_user
# from .views.better_views import UserListCreateApiView,UserRetrieveUpdateDestroyApiView
from .views.custom_api_views import UserListCreateApiView
urlpatterns = [
    # path('',say_hello),
    # path('',UserListCreateApiView.as_view()),
    # path('say_hello/<name>',say_hello_with_name),
    # path('say_hello/<name>',UserListCreateApiView.as_view()),

    # path('users/', UserListCreateAPIView.as_view()),
    path('users/', UserListCreateApiView.as_view()),
    path('admin/', admin.site.urls),

    # path('users/',users),
    # path('users/',UserListCreateApiView.as_view()),
    # path('users/<id>',get_or_update_or_delete_user),
    # path('users/<id>',UserListCreateApiView.as_view()),
    # path('users/<id>/',UserRetrieveUpdateDestroyApiView.as_view()),

]
