"""商品模块路由"""
from django.urls import path
from . import views

urlpatterns = [
    path("index/", views.index, name="index"),  # 首页
    path("detail/", views.detail, name="goods_detail"),  # 商品详情
    path("goods/", views.goods_list, name="goods_list"),  # 商品列表
    path('cart/show_cart/', views.show_cart, name='show_cart'),
]