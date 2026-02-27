from django.urls import path
from . import views

urlpatterns = [
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-home/", views.admin_index, name="admin_index"),
    path("category/",views.category,name="category"),
    path("subcategory/",views.subcategory,name="subcategory")
]