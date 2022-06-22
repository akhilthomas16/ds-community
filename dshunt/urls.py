"""dshunt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', views.post_list, name='home'),

    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),

    path('', views.post_list, name="post-list"),
    path('post/', views.PostSubmitPageView.as_view(), name='post-submit'),

    path('books/new/', views.BookCreateView.as_view(), name='book-create'),
    # path('videos/new/', views.video_create, name='video-create'),
    # path('books/new/', views.BookCreateView.as_view(), name='tutorial-create'),
    # path('books/new/', views.BookCreateView.as_view(), name='podcast-episode--create'),

    # category
    path('category/', views.category, name='category'),

    # vote
    path('post/<int:id>/vote', views.Vote.as_view(), name="postvote"),
]
