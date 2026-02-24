from django .urls import path
from .import views

urlpatterns=[
    path('register/',views.user_register,name='register'),
    path('login/',views.user_login,name='login'),
    path('profile/',views.user_profile,name='profile'),
    path('logout/',views.user_logout,name='logout'),
    path('home/',views.user_home,name='home'),
    path('wishlist/',views.user_wishlist,name='wishlist'),
    path('cart/',views.user_cart,name='cart'),
    path('myorders/',views.user_orders,name='myorders'),
]       