"""商品模块视图"""
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import GoodsCategory, GoodsInfo

import json
from django.http import HttpRequest

def get_cart_info_from_cookie(request: HttpRequest) -> dict:
    cart_str = request.COOKIES.get('cart', '')
    try:
        cart_dict = json.loads(cart_str) if cart_str else {}
    except json.JSONDecodeError:
        cart_dict = {}

    for key, value in request.COOKIES.items():
        if key.isdigit() and value.isdigit():
            cart_dict[key] = int(value)

    total_count = sum(cart_dict.values())
    return {
        "cart_dict": cart_dict,
        "total_count": total_count,
        "total_price": 0
    }


def goods_list(request):
    # 获取分类ID
    cag_id = request.GET.get('cag')
    if not cag_id:
        return redirect('/')

    try:
        cag = GoodsCategory.objects.get(id=cag_id)
    except GoodsCategory.DoesNotExist:
        return redirect('/')

    # 查询商品
    goods_queryset = GoodsInfo.objects.filter(goods_cag_id=cag_id)

    # 分页
    paginator = Paginator(goods_queryset, 10)
    page_num = request.GET.get('page', 1)
    page_data = paginator.get_page(page_num)

    #查询所有分类（给左侧分类菜单用）
    categories = GoodsCategory.objects.all()

    # 获取购物车信息
    cart_info = get_cart_info_from_cookie(request)

    #变量名 100% 匹配你的模板！！！
    return render(request, 'goods/list.html', {
        'current_cag': cag,  # 模板用的 current_cag
        'cag_id': cag_id,  # 模板分页需要
        'page_data': page_data,  # 模板循环商品用
        'categories': categories,  # 左侧全部分类
        **cart_info  # 购物车数量
    })


def index(request):
    categories = GoodsCategory.objects.all()
    for cag in categories:
        cag.goods_list = cag.goodsinfo_set.order_by("-id")[:4]

    cart_info = get_cart_info_from_cookie(request)

    return render(request, "index.html", {
        "categories": categories,
        **cart_info
    })

def show_cart(request: HttpRequest) -> HttpResponse:
    cart_info = get_cart_info_from_cookie(request)
    cart_dict = cart_info["cart_dict"]

    goods_list = []
    total_price = 0

    # 遍历购物车，把商品查出来
    for gid, count in cart_dict.items():
        try:
            goods = GoodsInfo.objects.get(id=gid)
            goods.count = count
            goods.amount = goods.goods_price * count
            goods_list.append(goods)
            total_price += goods.amount
        except GoodsInfo.DoesNotExist:
            continue

    cart_info["total_price"] = total_price

    return render(request, "cart/cart.html", {
        "goods_list": goods_list,
        **cart_info
    })

def detail(request: HttpRequest) -> HttpResponse:
    goods_id = request.GET.get("id")
    if not goods_id or not goods_id.isdigit():
        return render(request, "404.html", status=404)

    try:
        goods_data = GoodsInfo.objects.get(id=int(goods_id))
    except GoodsInfo.DoesNotExist:
        return render(request, "404.html", status=404)

    categories = GoodsCategory.objects.all()
    cart_info = get_cart_info_from_cookie(request)

    return render(request, 'goods/detail.html', {
        "categories": categories,
        "goods_data": goods_data,
        **cart_info
    })