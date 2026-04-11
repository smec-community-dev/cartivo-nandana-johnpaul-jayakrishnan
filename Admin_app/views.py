from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from functools import wraps
from django.contrib.auth.decorators import login_required
from Core_app.models import Category,SubCategory
from django.utils.text import slugify
from .models import Offer,Discount,OfferDiscountBridge,ProductOfferBridge,CategoryOfferBridge,ProductDiscountBridge
from django.contrib import messages
from Seller_app.models import Product
from Seller_app.models import SellerProfile

def admin_required(view_func):
    @wraps(view_func)
    @login_required(login_url="admin_login")
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, "role") and request.user.role == "ADMIN":
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse("You are not authorized to access this page.")
    return wrapper

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
        
            if user.role == "ADMIN":  
        
                login(request, user)
                return redirect("admin_index")
            else:
                return HttpResponse("You are not an Admin")
        else:
            return HttpResponse("Invalid Username or Password")

    return render(request, "adminlogin.html")

@admin_required
def admin_index(request):
    return render(request, "admin_index.html")


@admin_required
def add_category(request):

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        slug = slugify(name)

        if Category.objects.filter(slug=slug).exists():
            return render(request, "add_category.html", {
                "error": "Category already exists!"
            })

        Category.objects.create(
            name=name,
            slug=slug,
            description=description
        )

        return redirect("category")

    return render(request, "add_category.html")


def category(request):
    categories = Category.objects.all()
    return render(request, "category.html", {"categories": categories})

def category_toggle(request, id):
    category = Category.objects.get(id=id)

    if category.is_active:
        category.is_active = False
    else:
        category.is_active = True

    category.save()

    return redirect("category")

@admin_required
def add_subcategory(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all().order_by("-id")

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        category= Category.objects.get(id=request.POST.get("category"))

        
        slug = slugify(name)

        
        SubCategory.objects.create(
                category=category,   
                name=name,
                slug=slug,
                description=description,
                
            )

        return redirect("add_subcategory")   

    
    return render(request, "add-sub_category.html", {"categories": categories,"subcategories": subcategories})
    
def subcategory(request):
    subcategories = SubCategory.objects.all()
    return render(request, "sub_category.html", {"subcategories": subcategories})

def subcategory_toggle(request, id):
    subcategory = SubCategory.objects.get(id=id)

    if subcategory.is_active:
        subcategory.is_active = False
    else:
        subcategory.is_active = True

    subcategory.save()

    return redirect("subcategory")

    
    

def add_offer(request):
    offers = Offer.objects.all().order_by("-id")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if title and start_date and end_date:
            Offer.objects.create(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                
            )
            return redirect("offer_view")

    return render(request, "create_offer.html", {"offers": offers})

def view_offer(request):
    offers = Offer.objects.all()
    return render(request,"offer.html",{"offers":offers})

def offer_delete(request, id):
    offer = Offer.objects.get(id=id)
    offer.delete()
    return redirect("offer_view")



def add_discount(request):
    discounts = Discount.objects.all().order_by("-id")

    if request.method == "POST":
        name = request.POST.get("name")
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")

        if name and discount_type and discount_value:
            Discount.objects.create(
                name=name,
                discount_type=discount_type,
                discount_value=discount_value
            )
            return redirect("discount_view")

    return render(request, "add_discount.html", {"discounts": discounts})


def discount_view(request):
    discounts = Discount.objects.all().order_by("-id")
    return render(request, "discount.html", {"discounts": discounts})


def discount_delete(request, id):
    discount = Discount.objects.get(id=id)
    discount.delete()
    return redirect("discount_view")

from .models import Coupon

def add_coupon(request):
    coupons = Coupon.objects.all().order_by("-id")

    if request.method == "POST":
        code = request.POST.get("code")
        discount_value = request.POST.get("discount_value")
        valid_from = request.POST.get("valid_from")
        valid_to = request.POST.get("valid_to")
        usage_limit = request.POST.get("usage_limit")

        if code and discount_value:
            Coupon.objects.create(
                code=code,
                discount_value=discount_value,
                valid_from=valid_from,
                valid_to=valid_to,
                usage_limit=usage_limit
            )
            return redirect("coupon_view")

    return render(request, "add_coupon.html", {"coupons": coupons})

def view_coupon(request):
    coupons = Coupon.objects.all()
    return render(request,"coupon.html",{"coupons": coupons})

def coupon_delete(request, id):
    coupon = Coupon.objects.get(id=id)
    coupon.delete()
    return redirect("coupon_view")


def offer_discount_bridge(request):
    offers = Offer.objects.all()
    discounts = Discount.objects.all()
    bridges = OfferDiscountBridge.objects.all()

    if request.method == "POST":
        offer_id = request.POST.get("offer")
        discount_id = request.POST.get("discount")

        OfferDiscountBridge.objects.create(
            offer_id=offer_id,
            discount_id=discount_id
        )

        messages.success(request, "Offer Discount Linked")
        return redirect("offer_discount_bridge")

    return render(request, "offer_discount_bridge.html", {
        "offers": offers,
        "discounts": discounts,
        "bridges": bridges
    })


def product_offer_bridge(request):
    products = Product.objects.all()
    offers = Offer.objects.all()
    bridges = ProductOfferBridge.objects.all()

    if request.method == "POST":
        product_id = request.POST.get("product")
        offer_id = request.POST.get("offer")

        ProductOfferBridge.objects.create(
            product_id=product_id,
            offer_id=offer_id
        )

        messages.success(request, "Product Offer Linked")
        return redirect("product_offer_bridge")

    return render(request, "product_offer_bridge.html", {
        "products": products,
        "offers": offers,
        "bridges": bridges
    })
    

def category_offer_bridge(request):
    category = Category.objects.all()
    offer = Offer.objects.all()
    bridges = CategoryOfferBridge.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get("category_id")
        offer_id = request.POST.get("offer_id")
        if category_id and offer_id:
            CategoryOfferBridge.objects.create(
                category_id = category_id,
                offer_id = offer_id,
        )
        messages.success(request,"category offer linked")
        return redirect("category_offer_bridge")
        
    return render(request,"category_offer_bridge.html",{
        "category" : category,
        "offer" : offer,
        "bridges" : bridges,
    })
    
def Product_Discount_Bridge(request):

    product = Product.objects.all()
    discount = Discount.objects.all()
    bridge = ProductDiscountBridge.objects.all()

    if request.method == "POST":

        product_id = request.POST.get("product_id")
        discount_id = request.POST.get("discount_id")

        if product_id and discount_id:

            ProductDiscountBridge.objects.create(
                product_id=product_id,
                discount_id=discount_id
            )

            messages.success(request, "Product Discount Linked")

            return redirect("ProductDiscountBridge")

    return render(request, "ProductDiscountBridge.html", {
        "product": product,
        "discount": discount,
        "bridge": bridge
    })
        
def approve_seller(request,id):
    sellers = SellerProfile.objects.get(id=id)
    sellers.approved = True
    sellers.save()
    return redirect('pending_seller') 