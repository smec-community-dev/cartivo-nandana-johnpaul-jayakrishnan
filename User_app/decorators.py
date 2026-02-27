from django.shortcuts import redirect
from functools import wraps
from django.http import HttpResponseForbidden

def customer_required(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("unauthenticated",status=401)
            if request.user.role != 'customer':  
                return HttpResponseForbidden("You are not authorized to view this page.",status=401)
            return view_func(request, *args, **kwargs)
        return wrapper