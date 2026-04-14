from django.urls import path
from . import views

urlpatterns = [
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-home/", views.admin_index, name="admin_index"),
    path("category/",views.category, name="category"),
    path("add_category/",views.add_category,name="add_category"),
    path("category_toggle/<int:id>/", views.category_toggle, name="category_toggle"),
    path("subcategory/",views.subcategory,name="subcategory"),
    path("add_subcategory/",views.add_subcategory,name="add_subcategory"),
    path("subcategory_toggle/<int:id>/", views.subcategory_toggle, name="subcategory_toggle"),
    path("offer/", views.view_offer, name="offer_view"),
    path("add-offer/", views.add_offer, name="add_offer"),
    path("offer-delete/<int:id>/", views.offer_delete, name="offer_delete"),
    path("discount/", views.discount_view, name="discount_view"),
    path("add_discount/",views.add_discount,name="add_discount"),
    path("discount-delete/<int:id>/", views.discount_delete, name="discount_delete"),
    path("coupon/", views.view_coupon, name="coupon_view"),
    path("add_coupon/", views.add_coupon, name="add_coupon"),
    path("coupon-delete/<int:id>/", views.coupon_delete, name="coupon_delete"),
    path("offer-discount-bridge/",views.offer_discount_bridge,name="offer_discount_bridge"),
    path("product_offer_bridge/",views.product_offer_bridge,name="product_offer_bridge"),
    path("category_offer_bridge/",views.category_offer_bridge,name="category_offer_bridge"),
    path("Product_Discount_Bridge/",views.Product_Discount_Bridge,name="Product_Discount_Bridge"),
    path('pending-sellers/', views.pending_seller, name='pending-sellers'),
    path('approve-seller/<int:id>/', views.approve_seller, name='approve_seller'),
    path('reject-seller/<int:id>/', views.reject_seller, name='reject_seller'),

    
]