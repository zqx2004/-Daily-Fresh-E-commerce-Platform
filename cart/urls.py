"""购物车/订单模块路由"""
from django.urls import path
from . import views

urlpatterns = [
    path("add_cart/", views.add_cart, name="add_cart"),  # 添加购物车
    path("show_cart/", views.show_cart, name="show_cart"),  # 展示购物车
    path("remove_cart/", views.remove_cart, name="remove_cart"),  # 移除购物车商品
    path("place_order/", views.place_order, name="place_order"),  # 订单确认
    path("submit_order/", views.submit_order, name="submit_order"),  # 提交订单
    path("submit_success/", views.submit_success, name="submit_success"),  # 订单成功
]