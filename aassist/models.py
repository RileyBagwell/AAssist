from django.db import models
from django.contrib.auth.models import User


class Drink(models.Model):
    name = models.CharField(max_length=200)
    alcohol_content = models.FloatField(help_text="Alcohol content as percentage (e.g., 5.0 for 5%)")
    volume_ml = models.IntegerField(help_text="Volume in milliliters")
    calories_per_100ml = models.IntegerField(help_text="Calories per 100ml")
    category = models.CharField(max_length=100, choices=[
        ('beer', 'Beer'),
        ('wine', 'Wine'),
        ('spirits', 'Spirits'),
        ('cocktail', 'Cocktail'),
        ('other', 'Other')
    ])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.alcohol_content}%)"

    @property
    def total_calories(self):
        return int((self.calories_per_100ml * self.volume_ml) / 100)

    @property
    def alcohol_units(self):
        return round((self.alcohol_content * self.volume_ml * 0.789) / 1400, 2)


class DrinkConsumption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    consumed_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1, help_text="Number of drinks consumed")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.drink.name} at {self.consumed_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def total_alcohol_units(self):
        return round(self.drink.alcohol_units * self.quantity, 2)

    @property
    def total_calories(self):
        return self.drink.total_calories * self.quantity