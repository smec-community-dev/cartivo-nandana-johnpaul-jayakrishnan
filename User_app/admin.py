from django.contrib import admin
from Seller_app.models import Product
from Seller_app.models import ProductImage
from Seller_app.models import SellerProfile
from Seller_app.models import ProductVariant
from Core_app.models import SubCategory
from Core_app.models import Category

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(SellerProfile)
admin.site.register(SubCategory)
admin.site.register(Category)
admin.site.register(ProductVariant)
