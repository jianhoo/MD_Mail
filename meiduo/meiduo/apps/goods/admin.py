from django.contrib import admin

# Register your models here.
from . import models


class SKUAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)
