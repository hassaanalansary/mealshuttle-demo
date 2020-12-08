from django.core.management.base import BaseCommand
from matching_algo import models
from datetime import time
from random import randrange


class Command(BaseCommand):

    def handle(self, **options):
        self.create_restaurant_types()
        self.create_restaurants()
        self.create_companies()
        self.create_windows()
        self.create_orders()

    def create_restaurant_types(self):
        categories = ["Asian", "Bakeries", "Breakfast", "Burgers", "Crepe", "Donuts"]
        for category in categories:
            models.RestaurantType.objects.get_or_create(type=category)

    def create_restaurants(self):
        restaurants = [
            dict(name="Panda House", type="Asian", capacity=10),
            dict(name="Ralph", type="Bakeries", capacity=20),
            dict(name="Paul", type="Breakfast", capacity=30),
            dict(name="Mince", type="Burgers", capacity=25),
            dict(name="City Crepe", type="Crepe", capacity=40),
            dict(name="Dunkin Donuts", type="Donuts", capacity=11),
        ]
        for rest in restaurants:
            type = models.RestaurantType.objects.get(type=rest.pop('type'))
            obj, created = models.Restaurant.objects.get_or_create(name=rest['name'], capacity=rest['capacity'],
                                                                   type=type)

    def create_companies(self):
        companies = [
            dict(name='Microsoft', break_hour=time(hour=10)),
            dict(name='Amazon', break_hour=time(hour=14)),
            dict(name='Google', break_hour=time(hour=16)),
            dict(name='Facebook', break_hour=time(hour=11)),
        ]
        for company in companies:
            models.Company.objects.get_or_create(defaults=company, break_hour=company['break_hour'])

    def create_windows(self):
        x = models.Restaurant.objects.filter()
        for rest in x:
            start = randrange(16)
            end = start + 8
            if not rest.restaurantwindow_set.exists():
                rest.restaurantwindow_set.create(window_start=f"{start}:00", window_end=f"{end}:00")

    def create_orders(self):
        for _ in range(15):
            company_no = randrange(models.Company.objects.all().count())
            restaurant_no = randrange(models.Restaurant.objects.all().count())
            order = models.Order.objects.create(restaurant=models.Restaurant.objects.all()[restaurant_no],
                                                company=models.Company.objects.all()[company_no])
            order.orderitem_set.create(item="Test", qty=randrange(40), price=randrange(10))

