"""购物车/订单模块视图（100%修复版，适配旧表、旧字段、无报错）"""
import uuid
import json
from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpRequest
from django.utils import timezone
from goods.models import GoodsInfo
from goods.views import get_cart_info_from_cookie
from .models import OrderInfo, OrderGoods


def add_cart(request: HttpRequest) -> HttpResponse:
    goods_id = request.GET.get("id")
    count = int(request.GET.get("count", 1))

    if not goods_id or not goods_id.isdigit():
        prev_url = request.META.get("HTTP_REFERER", "/index/")
        return redirect(prev_url)

    prev_url = request.META.get("HTTP_REFERER", "/index/")
    response = redirect(prev_url)

    try:
        goods_id_int = int(goods_id)
        GoodsInfo.objects.get(id=goods_id_int)
    except (ValueError, GoodsInfo.DoesNotExist):
        return response

    cart_info = get_cart_info_from_cookie(request)
    cart_dict = cart_info["cart_dict"]

    goods_id_str = str(goods_id_int)
    cart_dict[goods_id_str] = cart_dict.get(goods_id_str, 0) + count

    response.set_cookie("cart", json.dumps(cart_dict), max_age=60 * 60 * 24 * 7, httponly=True)
    response.set_cookie(goods_id_str, cart_dict[goods_id_str], max_age=60 * 60 * 24 * 7, httponly=True)
    return response


def show_cart(request):
    cart_str = request.COOKIES.get('cart', '{}')
    cart_dict = json.loads(cart_str)

    goods_list = []
    total_price = 0
    total_count = 0

    for goods_id, count in cart_dict.items():
        goods = GoodsInfo.objects.get(id=goods_id)
        goods.count = count
        goods.amount = goods.goods_price * count
        goods_list.append(goods)
        total_price += goods.amount
        total_count += count

    return render(request, 'cart/cart.html', {
        'goods_list': goods_list,
        'total_price': total_price,
        'total_count': total_count,
    })


def remove_cart(request: HttpRequest) -> HttpResponse:
    goods_id = request.GET.get("id")
    prev_url = request.META.get("HTTP_REFERER", "/cart/show_cart/")
    response = redirect(prev_url)

    if goods_id and goods_id.isdigit():
        cart_info = get_cart_info_from_cookie(request)
        cart_dict = cart_info["cart_dict"]

        if goods_id in cart_dict:
            del cart_dict[goods_id]
            response.set_cookie("cart", json.dumps(cart_dict), max_age=60 * 60 * 24 * 7)
        response.delete_cookie(goods_id)

    return response


def place_order(request: HttpRequest) -> HttpResponse:
    cart_info = get_cart_info_from_cookie(request)
    cart_dict = cart_info["cart_dict"]

    if not cart_dict:
        return redirect("/cart/show_cart/")

    cart_goods_list = []
    total_price = 0
    total_count = 0
    freight = 10

    for gid, count in cart_dict.items():
        try:
            goods = GoodsInfo.objects.get(id=gid)
            goods.count = count
            goods.amount = goods.goods_price * count
            cart_goods_list.append(goods)
            total_price += goods.amount
            total_count += count
        except GoodsInfo.DoesNotExist:
            continue

    actual_price = total_price + freight
    order_sn = f"TT{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"

    return render(request, "place_order.html", {
        "cart_goods_list": cart_goods_list,
        "total_count": total_count,
        "total_price": total_price,
        "freight": freight,
        "actual_price": actual_price,
        "order_sn": order_sn,
    })


def submit_order(request: HttpRequest) -> HttpResponse:
    # 只处理POST请求，确保表单数据正常接收
    if request.method != "POST":
        return redirect("/cart/place_order/")

    # 1. 获取用户表单提交的真实数据
    address = request.POST.get("addr", "")
    receiver = request.POST.get("recv", "")
    phone = request.POST.get("tele", "")
    remark = request.POST.get("extra", "")

    # 2. 获取购物车数据
    cart_info = get_cart_info_from_cookie(request)
    cart_dict = cart_info["cart_dict"]

    if not cart_dict:
        return redirect("/cart/show_cart/")

    # 3. 生成唯一订单号
    order_sn = f"TT{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"

    # 4. 创建订单（用用户真实填写的数据，不再硬编码！）
    order = OrderInfo.objects.create(
        order_sn=order_sn,
        address=address,          # 用户填的地址
        receiver=receiver,        # 用户填的收货人
        phone=phone,              # 用户填的电话
        freight=10,               # 固定运费10元
        remark=remark,            # 用户填的备注
        status=1
    )

    # 5. 创建订单商品
    for gid, count in cart_dict.items():
        try:
            goods = GoodsInfo.objects.get(id=gid)
            OrderGoods.objects.create(
                goods=goods,
                quantity=count,
                order=order
            )
        except GoodsInfo.DoesNotExist:
            continue

    # 6. 清空购物车，跳转到成功页
    response = redirect("/cart/submit_success/")
    response.set_cookie("cart", "{}", max_age=60*60*24*7)
    # 同步删除旧版单个商品Cookie
    for gid in cart_dict.keys():
        response.delete_cookie(gid)
    # 保存最新订单号，确保成功页获取的是当前订单
    response.set_cookie("latest_order_sn", order_sn, max_age=60*5)

    return response


def submit_success(request):
    # 优先从Cookie获取刚提交的订单号
    order_sn = request.COOKIES.get("latest_order_sn", "")
    if order_sn:
        try:
            order = OrderInfo.objects.get(order_sn=order_sn)
        except OrderInfo.DoesNotExist:
            order = OrderInfo.objects.last()
    else:
        order = OrderInfo.objects.last()

    # 获取订单商品列表
    order_goods_list = OrderGoods.objects.filter(order=order)

    total_num = 0
    total_money = 0

    # 计算每个商品的小计，累加总金额
    for item in order_goods_list:
        item.amount = item.goods.goods_price * item.quantity
        total_num += item.quantity
        total_money += item.amount

    return render(request, 'success.html', {
        'order_info': order,
        'order_goods_list': order_goods_list,
        'total_num': total_num,
        'total_money': total_money,
    })