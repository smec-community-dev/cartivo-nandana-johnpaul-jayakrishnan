from django.contrib import admin
from Seller_app.models import Product
from .models import Order,OrderItem,Cart,CartItem
from Seller_app.models import ProductImage,SellerProfile,ProductVariant,Attribute,AttributeOption,VariantAttributeBridge
from Core_app.models import SubCategory,Category
from Admin_app.models import Offer,Discount,OfferDiscountBridge,ProductOfferBridge,Coupon
# Register your models here.
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(SellerProfile)
admin.site.register(SubCategory)
admin.site.register(Category)
admin.site.register(ProductVariant)
admin.site.register(Attribute)
admin.site.register(AttributeOption)
admin.site.register(VariantAttributeBridge)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon)