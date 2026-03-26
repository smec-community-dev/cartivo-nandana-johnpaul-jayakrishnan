from django.shortcuts import redirect
from functools import wraps
from django.http import HttpResponseForbidden

def customer_login_required(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect ('login')
            if request.user.role != 'CUSTOMER':  
                return HttpResponseForbidden("You are not authorized to view this page.",status=401)
            return view_func(request, *args, **kwargs)
        return wrapper

def customer_required(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user =  request.user
            if request.user.role != 'CUSTOMER':  
                return HttpResponseForbidden("You are not authorized to view this page.",status=401)
            return view_func(request, *args, **kwargs)
        return wrapper