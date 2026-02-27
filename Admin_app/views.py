from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from functools import wraps
from django.contrib.auth.decorators import login_required
from Core_app.models import Category,SubCategory
from django.utils.text import slugify

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
def category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        
        if name and description:
            slug = slugify(name)
            
            if Category.objects.filter(slug=slug).exists():
                return HttpResponse("Category already exists ")
            
            Category.objects.create(
                name = name,
                slug = slug,
                description = description
            )
            return HttpResponse("Category add successfully ")
        return redirect("category")
        
    categories = Category.objects.all().order_by("-id")
        
    return render(request,"category.html",{"categories":categories})


@admin_required
def subcategory(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        
        if name and description:
            slug = slugify(name)
            
            if Category.objects.filter(slug=slug).exists():
                return HttpResponse("SubCategory already exists ")
            
            Category.objects.create(
                name = name,
                slug = slug,
                description = description
            )
            return HttpResponse("SubCategory add successfully ")
        return redirect("subcategory")
        
    categories = Category.objects.all().order_by("-id")
        
    return render(request,"sub_category.html",{"categories":categories})


    