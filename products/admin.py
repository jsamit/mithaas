from django.contrib import admin

from .models import Product,Variation,ProductImages,Category,ProductFeatured

class ProductImagesInline(admin.TabularInline):
	model = ProductImages
	extra = 1

class VariationInline(admin.TabularInline):
	model = Variation
	extra = 0

class ProductAdmin(admin.ModelAdmin):
	list_display = ['__str__','price']
	inlines = [
		VariationInline,
		ProductImagesInline,
	]
	class Meta:
		model = Product

admin.site.register(Product,ProductAdmin)
# admin.site.register(Variation)
# admin.site.register(ProductImages)
admin.site.register(Category)
admin.site.register(ProductFeatured)
