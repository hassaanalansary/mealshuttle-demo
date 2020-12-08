from datetime import time
from django.db import models
from django.db.models import Sum, Avg, Count, Q, F,  QuerySet


class RestaurantWindowQuerySet(QuerySet):
    def delivery_window_around(self, delivery_window: time) -> QuerySet:
        no_midnight = self.filter(Q(window_start__lte=F('window_end')), Q(window_start__lte=delivery_window),
                                  window_end__gte=delivery_window)
        # if the window spans midnight
        midnight = self.filter(Q(window_start__gt=F('window_end')),
                               Q(window_start__lte=delivery_window) | Q(window_end__gte=delivery_window))

        return no_midnight | midnight


class RestaurantType(models.Model):
    type = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.type


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(RestaurantType, on_delete=models.CASCADE)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class RestaurantWindow(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    window_start = models.TimeField()
    window_end = models.TimeField()
    objects = RestaurantWindowQuerySet.as_manager()

    def __str__(self):
        return f"{self.restaurant} {self.window_start} {self.window_end}"


class Company(models.Model):
    name = models.CharField(max_length=255)
    break_hour = models.TimeField()

    def __str__(self):
        return f"{self.name}"

    @property
    def avg_demand(self):
        return self.order_set.aggregate(avg_demand=Avg('total_qty')).get('avg_demand') or 0.0

    @property
    def matching_restaurants(self, limit: int = 3):
        restaurants_matching_window = RestaurantWindow.objects.delivery_window_around(self.break_hour).values_list(
            "restaurant_id", flat=True)

        query = Restaurant.objects.annotate(
            exposures=Count("exposure__id", filter=Q(exposure__company=self)),
        ).filter(
            capacity__gt=self.avg_demand,
            id__in=restaurants_matching_window
        ).order_by(
            'exposures'
        )
        typed_restaurant = {}
        for item in query[:limit]:
            typed_restaurant.setdefault(item.type_id, item)
            Exposure.objects.create(company=self, restaurant=item)
        return [f"({x.name}, Exposures: {x.exposures} Capacity:{x.capacity} Type:{x.type})" for x in
                typed_restaurant.values()]


class OrderManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().annotate(total_qty=Sum('orderitem__qty'))
        return qs


class Order(models.Model):
    date_placed = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)

    objects = OrderManager()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.CharField(max_length=255)  # should have a proper Item object, but this is out of scope
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=19, decimal_places=2)


class Exposure(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_placed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} {self.restaurant}"
