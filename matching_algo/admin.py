from django.contrib import admin
from django.utils.html import format_html
from .models import *


@admin.register(RestaurantType, Restaurant, RestaurantWindow, Order, OrderItem, Exposure)
class Configure(admin.ModelAdmin):
    pass


@admin.register(Company)
class AdminMessage(admin.ModelAdmin):
    model = Company
    list_display = ['name', 'break_hour', 'avg_demand', 'matching_restaurants']

    def matching_restaurants(self, obj):
        return format_html("<br>".join(obj.matching_restaurants))

