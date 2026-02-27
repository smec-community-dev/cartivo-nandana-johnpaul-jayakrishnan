from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import User
from User_app.decorators import customer_required
from Seller_app.models import Product,ProductImage,ProductVariant,VariantAttributeBridge


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
        
        data_user = User(username=username,email=email,phone_number=phone_number,password=make_password(password),profile_image=profile_image)
        data_user.save()
        return redirect("login") 
    return render (request,"user/register_user.html")

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(email=email).first()
        if user_obj:
            user = authenticate(request,username=user_obj.username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                messages.error(request,"invalid username or password")
    return render(request,"user/user_login.html")

@login_required
def user_profile(request):
    user = request.user
    return render(request,'user/user_profile.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

def user_home(request):
    products = Product.objects.prefetch_related('variants__images').filter(is_active=True, approval_status='APPROVED')
    return render(request,'user/home.html',{'products':products})

@login_required
def user_wishlist(request):
    return render(request,'user/wishlist.html')

@login_required
def user_cart(request):
    return render(request,'user/cart.html')

@login_required
def user_orders(request):
    return render(request,'user/myorders.html')

@login_required
def user_address(request):
    return render(request,'user/add_address.html')

@login_required
def user_payment_method(request):
    return render(request,'user/payment_add.html')

@login_required
def user_product_view(request,id):
    variant = ProductVariant.objects.select_related('product').prefetch_related('images').get(id=id)
    return render(request,'user/product_view.html',{'variant':variant})