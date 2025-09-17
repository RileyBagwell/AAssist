from django.contrib import admin

from .models import Drink, DrinkConsumption


@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'alcohol_content', 'volume_ml', 'total_calories', 'alcohol_units']
    list_filter = ['category', 'alcohol_content']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(DrinkConsumption)
class DrinkConsumptionAdmin(admin.ModelAdmin):
    list_display = ['drink', 'quantity', 'consumed_at', 'total_alcohol_units', 'total_calories']
    list_filter = ['consumed_at', 'drink__category']
    search_fields = ['drink__name', 'notes']
    ordering = ['-consumed_at']