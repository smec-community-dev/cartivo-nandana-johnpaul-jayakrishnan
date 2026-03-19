from django .urls import path
from .import views

urlpatterns=[
    path('register/',views.user_register,name='register'),
    path('login/',views.user_login,name='login'),
    path('verify-email/<uidb64>/<token>/',views.user_verify_email,name='user_verify_email'),
    path('profile/',views.user_profile,name='profile'),
    path('logout/',views.user_logout,name='logout'),
    path('home/',views.user_home,name='home'),
    path('product_view/<int:id>/',views.user_product_view,name='product_view'),
    path('products/',views.user_product_filter_page,name='product_filter'),

    path('wishlist/',views.user_wishlist_display,name='wishlist'),
    path('wishlist_add/<int:id>/    ',views.user_wishlist,name='wishlist_add'),
    path('wishlist_item_delete/<int:id>/',views.user_wishlist_item_delete,name='wishlist_item_delete'),
    
    path('address/',views.user_address_display,name='address'),
    path('user_address_add/',views.user_address_add,name='user_address_add'),
    path('user_address_edit/<int:id>/',views.user_address_edit,name='user_address_edit'),

    path('payment_method/',views.user_payment_method,name='payment_method'),
    path('payment_choice',views.user_payment_choice,name='payment_choice'),

    path('cart/',views.user_cart_display,name='cart'),
    path('add_cart/<int:id>/',views.user_cart,name='add_cart'),
    path('add_cart_quantity/<int:id>/',views.user_cart_add_quantity,name='add_cart_quantity'),
    path('sub_cart_quantity/<int:id>/',views.user_cart_substract_quantity,name='sub_cart_quantity'),      
    path('delete_cart_item/<int:id>/',views.user_cart_item_delete,name='delete_cart_item'),

    path('myorders/',views.user_orders,name='myorders'),
    path('user_order_confirm/<int:id>/',views.user_order_confirmation,name='user_order_confirm'),
    path('user_order_cart_confirm/<int:id>/',views.user_order_cart_confirmation,name='user_order_cart_confirm'),
    path('user_order_display/',views.user_order_display,name='user_order_display'),
    path('add_order_quantity/<int:id>/',views.user_order_add_quantity,name='add_order_quantity'),
    path('sub_order_quantity/<int:id>/',views.user_order_substract_quantity,name='sub_order_quantity'),      
    path('delete_order_item/<int:id>/',views.user_order_item_delete,name='delete_order_item'),
]       