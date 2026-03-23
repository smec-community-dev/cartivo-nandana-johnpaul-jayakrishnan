from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from .models import User,Cart,CartItem,Order,OrderItem,Wishlist,WishlistItem
from User_app.decorators import customer_login_required,customer_required
from Seller_app.models import Product,ProductImage,ProductVariant,VariantAttributeBridge,Attribute
from Core_app.models import Address, Category, SubCategory
from Admin_app.models import Coupon
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import JsonResponse
import json

# Create your views here.

def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get('password')
        profile_image=request.FILES.get('profile_image')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")
        
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists")
            return redirect("register")
        
        data_user = User(
            username=username,
            email=email,
            phone_number=phone_number,
            password=make_password(password),
            profile_image=profile_image,
            is_active=False,
        )
        data_user.save()
        
        uidb64 = urlsafe_base64_encode(force_bytes(data_user.pk))
        token = default_token_generator.make_token(data_user)
        verify_url = request.build_absolute_uri(
            reverse('user_verify_email', kwargs={'uidb64': uidb64, 'token': token})
        )
        subject = "Verify your Cartivo account"
        message = (
            f"Hi {data_user.username},\n\n"
            "Thanks for registering on Cartivo.\n"
            "Please verify your email by clicking the link below:\n\n"
            f"{verify_url}\n\n"
            "If you didn't create this account, you can ignore this email.\n"
        )
        send_mail(
            subject,
            message,
            getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@cartivo.local',
            [data_user.email],
            fail_silently=False,
        )

        messages.success(request, "Account created! Please check your email to verify your account before logging in.")
        return redirect("login")
    return render (request,"user/register_user.html")

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(email=email).first()
        if user_obj:
            if not user_obj.is_active:
                messages.error(request, "Please verify your email before logging in.")
                return redirect('login')
            user = authenticate(request,username=user_obj.username,password=password)
            if user is not None:
                if user_obj.role == 'CUSTOMER':
                    login(request,user)
                    return redirect('home')
                else:
                    messages.error(request,"you are not allowed to login as user")
            else:
                messages.error(request,"invalid username or password")
    return render(request,"user/user_login.html")

def user_verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
        messages.success(request, "Email verified successfully. You can now log in.")
        return redirect('login')

    messages.error(request, "Verification link is invalid or has expired.")
    return redirect('register')

@customer_login_required
def user_profile(request):
    user = request.user
    if request.method=='POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        gender=request.POST.get('gender')

        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, "Username already exists")
            return redirect("register")
        else:
            messages.success(request, "Username updated")
        
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Email already exists")
            return redirect("register")
        else:
            messages.success(request, "Email updated")
    
        if User.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
            messages.error(request, "Phone number already exists")
            return redirect("register")
        else:
            messages.success(request, "Phone Number updated")

        user.username=username
        user.email=email
        user.phone_number=phone_number
        user.gender=gender
        user.save()

    return render(request,'user/user_profile.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

def user_home(request):
    user = request.user
    products = products = Product.objects.filter(is_active=True,approval_status='APPROVED').prefetch_related('variants__images')
    return render(request,'user/home.html',{'products':products})

@customer_login_required
def user_product_filter(request):
    q = (request.GET.get('q') or '').strip()
    brand = (request.GET.get('brand') or '').strip()
    category_id = (request.GET.get('category') or '').strip()
    subcategory_id = (request.GET.get('subcategory') or '').strip()
    sort = (request.GET.get('sort') or '').strip()

    products = Product.objects.filter(is_active=True, approval_status='APPROVED').select_related(
        'subcategory', 'subcategory__category'
    ).prefetch_related('variants__images')

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) | 
            Q(brand__icontains=q) |
            Q(model_number__icontains=q)
        )

    if brand:
        products = products.filter(brand__iexact=brand)

    if subcategory_id.isdigit():
        products = products.filter(subcategory_id=int(subcategory_id))
    elif category_id.isdigit():
        products = products.filter(subcategory__category_id=int(category_id))

    if sort == 'price_low':
        products = products.order_by('variants__cost_price')
    elif sort == 'price_high':
        products = products.order_by('-variants__cost_price')
    elif sort == 'new':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')

    categories = Category.objects.all().order_by('name')
    subcategories = SubCategory.objects.select_related('category').all().order_by('name')
    brands = Product.objects.filter(is_active=True, approval_status='APPROVED').exclude(brand__isnull=True).exclude(brand__exact='').values_list('brand', flat=True).distinct().order_by('brand')

    context = {
        'products': products,
        'q': q,
        'brand': brand,
        'category_id': category_id,
        'subcategory_id': subcategory_id,
        'sort': sort,
        'categories': categories,
        'subcategories': subcategories,
        'brands': brands,
    }
    return render(request, 'user/product_filter_page.html', context)

@customer_login_required
def user_wishlist(request,id):
    user_name=request.user
    variant=ProductVariant.objects.get(id=id)
    wishlist, created=Wishlist.objects.get_or_create(user=user_name)
    wishlist_item=WishlistItem.objects.filter(wishlist=wishlist,variant=variant).first()
    if wishlist_item:
            messages.error(request,"item already in your wishlist")
    else:
        add_to_wishlist=WishlistItem(wishlist=wishlist,variant=variant)
        add_to_wishlist.save()
    previous_url = request.META.get('HTTP_REFERER')
    return redirect(previous_url)

@customer_login_required
def user_wishlist_item_delete(request,id):
    variant=ProductVariant.objects.get(id=id)
    Wishlist_item=WishlistItem.objects.get(variant=variant)
    Wishlist_item.delete()
    return redirect('wishlist')

@customer_login_required
def user_wishlist_display(request):    
    user_name=request.user
    wishlist, created=Wishlist.objects.get_or_create(user=user_name)
    wishlist_item=WishlistItem.objects.filter(wishlist=wishlist)
    return render(request,'user/wishlist.html',{'wishlist_item':wishlist_item})

@customer_login_required
def user_cart(request,id):
    user_name=request.user
    variant=ProductVariant.objects.get(id=id)
    cart, created=Cart.objects.get_or_create(user=user_name)
    cart_item=CartItem.objects.filter(cart=cart,variant=variant).first()
    if cart_item:
        if cart_item.quantity <= variant.stock_quantity:
            cart_item.quantity += 1
            cart_item.save()
            cart.total_amount=cart_item.price_at_time*cart_item.quantity
            cart.total_amount += variant.cost_price
            cart.save()
        else:
            messages.error(request,"item stock out")
    else:
        cart_item=CartItem(cart=cart,variant=variant,quantity=1,price_at_time=variant.cost_price)
        cart_item.save()
        cart.total_amount=variant.cost_price
        cart.save()
    previous_url = request.META.get('HTTP_REFERER')
    return redirect(previous_url)

@customer_login_required
def user_cart_add_quantity(request,id):
    variant=ProductVariant.objects.get(id=id)
    cart=Cart.objects.get(user=request.user)
    cart_item=CartItem.objects.get(cart=cart,variant=variant)
    if cart_item.quantity < variant.stock_quantity:
        cart_item.quantity += 1
        cart_item.save()
        cart.total_amount += variant.cost_price
        cart.save()
    else:
        messages.error(request,"item stock out")
    return redirect('cart')

@customer_login_required
def user_cart_substract_quantity(request,id):
    variant=ProductVariant.objects.get(id=id)
    cart=Cart.objects.get(user=request.user)
    cart_item=CartItem.objects.get(cart=cart,variant=variant)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        cart.total_amount -= variant.cost_price
        cart.save()
    else:
        cart_item.delete()
        cart.total_amount -= variant.cost_price
        cart.save()
    return redirect('cart')

@customer_login_required
def user_cart_item_delete(request,id):
    variant=ProductVariant.objects.get(id=id)
    cart=Cart.objects.get(user=request.user)
    cart_item=CartItem.objects.get(cart=cart,variant=variant)
    cart_item.delete()
    return redirect('cart')

@customer_login_required
def user_cart_display(request):    
    user_name=request.user
    cart=Cart.objects.filter(user=user_name).first()
    cart_item=CartItem.objects.filter(cart=cart)
    return render(request,'user/cart.html',{'cart_item':cart_item,'cart':cart})


@customer_login_required
def user_payment_method(request):
    return render(request,'user/payment_add.html')

def user_product_view(request, id):
    user = request.user
    variant = ProductVariant.objects.select_related('product').prefetch_related('images').get(id=id)
    variants = ProductVariant.objects.filter(product=variant.product).prefetch_related('images')
    attributebridge = VariantAttributeBridge.objects.filter(variant=variant)
    attributes = []
    for item in attributebridge:
        attribute = Attribute.objects.get(id=item.option.id)
        attributes.append(attribute)
    discount=(variant.cost_price*100)/variant.mrp
    discount_percentage=discount-100
    return render(request, 'user/product_view.html', {
                                                        'discount':discount_percentage,
                                                        'variant': variant,
                                                        'variants': variants,
                                                        'user': user,
                                                        'attribute': attributes
                                                        })

@customer_login_required
def user_payment_choice(request):
    user_name = request.user
    order = Order.objects.filter(user=user_name).first()
    order_item = OrderItem.objects.filter(order=order)

    if not order or not order_item.exists():
        messages.error(request, "No items in your order.")
        return redirect('user_order_display')

    total_discount = Decimal('0')
    for items in order_item:
        total_discount += items.discount_price * Decimal(items.quantity)

    handling_fee = Decimal('59')
    coupon_discount = Decimal('0')
    applied_coupon_code = ''
    applied = request.session.get('applied_coupon')

    if order and applied and applied.get('order_id') == order.id:
        code = applied.get('code', '').strip()
        if code:
            now = timezone.now()
            coupon = Coupon.objects.filter(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now,
            ).first()

            if coupon:
                discount_value = applied.get('discount_value') or coupon.discount_value
                coupon_discount = Decimal(str(discount_value))

                if coupon_discount < 0:
                    coupon_discount = Decimal('0')
                if coupon_discount > order.total_amount:
                    coupon_discount = order.total_amount

                applied_coupon_code = coupon.code
            else:
                request.session.pop('applied_coupon', None)

    amount_payable = (order.total_amount - coupon_discount + handling_fee)

    amount_paise = int(amount_payable * 100)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    })

    return render(request, 'user/payment.html', {
        'order': order,
        'order_item_count': order_item.count(),
        'total_discount': total_discount,
        'coupon_discount': coupon_discount,
        'handling_fee': handling_fee,
        'amount_payable': amount_payable,

        'payment': payment,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount_paise,
        'user':request.user,

        'applied_coupon_code': applied_coupon_code,
        'f_bag_total': float(order.total_amount),
        'f_total_discount': float(total_discount),
        'f_coupon_discount': float(coupon_discount),
        'f_handling_fee': float(handling_fee),
        'f_amount_payable': float(amount_payable),
    })

@customer_login_required
def user_orders(request):
    orders=Order.objects.filter(order_status='Processing')
    return render(request,'user/myorders.html',{"orders":orders})

@customer_login_required
def user_order_confirmation(request,id):
    user_name=request.user
    variant=ProductVariant.objects.get(id=id)
    order=Order.objects.filter(user=user_name).first()
    product_price=variant.cost_price
    if order:
        order_item=OrderItem.objects.filter(order=order).first()
        if order_item:
            order_item.delete()
            order.total_amount=0
            # if order_item.quantity < variant.stock_quantity:
            #     order_item.quantity += 1
            #     order_item.seller=variant.product.seller
            #     order_item.discount_price=variant.mrp-variant.cost_price
            #     order_item.save() 
            #     order.total_amount+=order_item.price_at_purchase
            #     order.save() 
            # else:     
            #     messages.error(request,"item stock out")
            order_item1=OrderItem(order=order,
                                  variant=variant,
                                  seller=variant.product.seller,
                                  discount_price=variant.mrp-variant.cost_price,
                                  price_at_purchase=product_price)
            order_item1.save()
            order.total_amount+=product_price
            order.save()
        else:
            order_item1=OrderItem(order=order,
                                  variant=variant,
                                  seller=variant.product.seller,
                                  discount_price=variant.mrp-variant.cost_price,
                                  price_at_purchase=product_price)
            order_item1.save()
            order.total_amount+=product_price
            order.save()
    else:
        order1=Order(user=user_name,total_amount=product_price)
        order1.save()
        order_item1=OrderItem(order=order1,
                              variant=variant,
                              seller=variant.product.seller,
                              discount_price=variant.mrp-variant.cost_price,
                              price_at_purchase=product_price)
        order_item1.save()
    return redirect('user_order_display')

@customer_login_required
def user_order_add_quantity(request,id):
    variant=ProductVariant.objects.get(id=id)
    order=Order.objects.get(user=request.user)
    order_item=OrderItem.objects.get(order=order,variant=variant)
    if order_item.quantity < variant.stock_quantity:
        order_item.quantity += 1
        order_item.save()
        order.total_amount += variant.cost_price
        order.save()
    else:
        messages.error(request,"item stock out")
    return redirect('user_order_display')

@customer_login_required
def user_order_substract_quantity(request,id):
    variant=ProductVariant.objects.get(id=id)
    order=Order.objects.get(user=request.user)
    order_item=OrderItem.objects.get(order=order,variant=variant)
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
        order.total_amount -= variant.cost_price
        order.save()
    else:
        order_item.delete()
        order.total_amount -= variant.cost_price
        order.save()
    return redirect('user_order_display')

@customer_login_required
def user_order_item_delete(request,id):
    variant=ProductVariant.objects.get(id=id)
    order=Order.objects.get(user=request.user)
    order_item=OrderItem.objects.get(order=order,variant=variant)
    order_item.delete()
    return redirect('user_order_display')

@customer_required
def user_order_display(request):   
    user_name=request.user
    order=Order.objects.filter(user=user_name).first()
    order_item=OrderItem.objects.filter(order=order)
    address=Address.objects.get(is_default=True)
    total_discount=0
    for items in order_item:
        total_discount+=items.discount_price*items.quantity
    
    handling_fee = Decimal('59')
    coupon_discount = Decimal('0')
    applied_coupon_code = ''

    applied = request.session.get('applied_coupon')

    if order and applied and applied.get('order_id') == order.id:
        code = applied.get('code', '').strip()

        if code:
            now = timezone.now()

            coupon = Coupon.objects.filter(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now
            ).first()

            if coupon:
                discount_value = applied.get('discount_value') or coupon.discount_value
                coupon_discount = Decimal(str(discount_value))

                if coupon_discount < 0:
                    coupon_discount = Decimal('0')

                if coupon_discount > order.total_amount:
                    coupon_discount = order.total_amount

                applied_coupon_code = coupon.code
            else:
                request.session.pop('applied_coupon', None)

    amount_payable = (order.total_amount - coupon_discount + handling_fee) if order else handling_fee

    return render(
        request,
        'user/order_confirmation.html',
        {
            'order_item': order_item,
            'total_discount': total_discount,
            'order': order,
            'address': address,
            'user': user_name,
            'coupon_discount': coupon_discount,
            'amount_payable': amount_payable,
            'handling_fee': handling_fee,
            'applied_coupon_code': applied_coupon_code,
        }
    )

@customer_login_required
def user_apply_coupon(request):
    if request.method != 'POST':
        return redirect('user_order_display')

    user_name = request.user
    order = Order.objects.filter(user=user_name).first()
    if not order:
        messages.error(request, "Order not found.")
        return redirect('user_order_display')

    coupon_code = (request.POST.get('coupon_code') or '').strip()
    if not coupon_code:
        messages.error(request, "Please enter a coupon code.")
        return redirect('user_order_display')

    now = timezone.now()
    coupon = Coupon.objects.filter(
        code__iexact=coupon_code,
        valid_from__lte=now,
        valid_to__gte=now
    ).first()

    if not coupon:
        messages.error(request, "Invalid or expired coupon.")
        return redirect('user_order_display')

    if coupon.used_count >= coupon.usage_limit:
        messages.error(request, "This coupon has reached its usage limit.")
        return redirect('user_order_display')

    prior = request.session.get('applied_coupon') or {}
    discount = Decimal(str(coupon.discount_value))
    if discount <= 0:
        messages.error(request, "This coupon is not applicable.")
        return redirect('user_order_display')

    if discount > order.total_amount:
        discount = order.total_amount

    already_applied = (
        prior.get('order_id') == order.id
        and (prior.get('code') or '').strip().lower() == coupon.code.strip().lower()
    )

    if not already_applied:
        coupon.used_count += 1
        coupon.save(update_fields=['used_count'])

    request.session['applied_coupon'] = {
        'order_id': order.id,
        'code': coupon.code,
        'discount_value': str(discount),
    }
    request.session.modified = True

    messages.success(request, f"Coupon applied: {coupon.code}")
    return redirect('user_order_display')

@customer_required
def user_order_cart_confirmation(request,id):
    user_name=request.user
    cart=Cart.objects.get(id=id)
    cart_item=CartItem.objects.filter(cart=cart)
    order=Order.objects.filter(user=user_name).first()     
    if cart_item:
        for i in cart_item:
            variant=i.variant
            product_price=variant.cost_price
            if order:
                order_item=OrderItem.objects.filter(order=order,variant=variant).first()
                if order_item:
                    if order_item.quantity < variant.stock_quantity:
                        order_item.quantity += 1
                        order_item.seller=variant.product.seller
                        order_item.save() 
                        order.total_amount+=order_item.price_at_purchase
                        order.save() 
                    else:     
                        messages.error(request,"item stock out")
                else:
                    order_item1=OrderItem(order=order,
                                          variant=variant,
                                          seller=variant.product.seller,
                                          price_at_purchase=product_price)
                    order_item1.save()
                    order.total_amount+=product_price
                    order.save() 
            else:
                order1=Order(user=user_name,total_amount=product_price)
                order1.save()
                print(order1.total_amount)
                order_item1=OrderItem(order=order1,
                                      variant=variant,
                                      seller=variant.product.seller,
                                      price_at_purchase=product_price)
                order_item1.save()
    else:
        messages.error(request,'zero items in your cart')
    return redirect('user_order_display')

@customer_login_required
def user_address_display(request):
    user_address=Address.objects.filter(user=request.user)
    return render(request,'user/add_address.html',{'user_address':user_address})

@customer_login_required
def user_address_add(request):
    if request.method=='POST':
        full_name=request.POST.get('full_name')
        phone_number=request.POST.get('phone_number')
        pincode=request.POST.get('pincode')
        locality=request.POST.get('locality')
        house_info=request.POST.get('house_info')
        city=request.POST.get('city')
        state=request.POST.get('state')
        country=request.POST.get('country')
        landmark=request.POST.get('landmark')
        address_type=request.POST.get('address_type')
        address_data=Address(user=request.user,
                             full_name=full_name,
                             phone_number=phone_number,
                             pincode=pincode,locality=locality,
                             house_info=house_info,
                             city=city,
                             state=state,
                             country=country,
                             landmark=landmark,
                             address_type=address_type,
                             )
        address_data.save()
    previous_url = request.META.get('HTTP_REFERER')
    return redirect(previous_url)

@customer_login_required
def user_address_edit(request,id):
    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == 'POST':
        address.full_name = request.POST.get('full_name') or address.full_name
        address.phone_number = request.POST.get('phone_number') or address.phone_number
        address.pincode = request.POST.get('pincode') or address.pincode
        address.locality = request.POST.get('locality') or address.locality
        address.house_info = request.POST.get('house_info') or address.house_info
        address.city = request.POST.get('city') or address.city
        address.state = request.POST.get('state') or address.state
        address.country = request.POST.get('country') or address.country
        address.landmark = request.POST.get('landmark') or address.landmark
        address.address_type = request.POST.get('address_type') or address.address_type

        required_fields = {
            'full_name': address.full_name,
            'phone_number': address.phone_number,
            'pincode': address.pincode,
            'locality': address.locality,
            'house_info': address.house_info,
            'city': address.city,
            'state': address.state,
            'country': address.country,
            'address_type': address.address_type,
        }
        missing = [k for k, v in required_fields.items() if not v]
        if missing:
            messages.error(request, "Please fill all required address fields.")
            return render(request, 'user/edit_address.html', {'address': address})

        address.save()
        messages.success(request, "Address updated successfully.")
        return redirect('address')

    return render(request, 'user/edit_address.html', {'address': address})


@customer_login_required
def select_address_default(request,id):
    user=request.user
    address=Address.objects.filter(user=user)
    print("hi")
    for i in address:
        if i.id==id:
            i.is_default=True
            i.save()
        elif i.id!=id:
            i.is_default=False
            i.save()
    return redirect('address')

def create_payment(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    amount = 50000

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render(request, "payment.html", {
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount
    })


@csrf_exempt
def razorpay_verify(request):
    if request.method == "POST":
        data = json.loads(request.body)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })



            return render(request,"user/payment_success.html")

        except:
            return JsonResponse({"status": "failed"})
