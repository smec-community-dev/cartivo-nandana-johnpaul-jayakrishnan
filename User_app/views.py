from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import User

# Create your views here.
def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get('password')
        profile_image=request.POST.get('profile_image')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")
        
        data_user = User(username=username,email=email,phone_number=phone_number,password=make_password(password),profile_image=profile_image)
        data_user.save()
        return redirect("login") 
    return render (request,"register_user.html")

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(email=email).first()
        if user_obj:
            user = authenticate(request,username=user_obj.username,password=password)
            if user is not None:
                login(request,user)
                return redirect('profile')
            else:
                messages.error(request,"invalid username or password")
    return render(request,"user_login.html")

@login_required
def user_profile(request):
    return render(request,'user_profile.html')

def user_logout(request):
    logout(request)
    return redirect('login')
