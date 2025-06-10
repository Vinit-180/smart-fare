from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

WEEKDAYS = [
    ("monday", "Monday"),
    ("tuesday", "Tuesday"),
    ("wednesday", "Wednesday"),
    ("thursday", "Thursday"),
    ("friday", "Friday"),
    ("saturday", "Saturday"),
    ("sunday", "Sunday"),
]

class PricingConfig(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DistanceBasePrice(models.Model):
    config = models.ForeignKey(PricingConfig, related_name="dbps", on_delete=models.CASCADE)
    weekday = models.CharField(choices=WEEKDAYS, max_length=10)
    up_to_kms = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("config", "weekday")

    def __str__(self):
        return f"{self.config.name} - {self.weekday}"

class DistanceAdditionalPrice(models.Model):
    config = models.ForeignKey(PricingConfig, related_name="daps", on_delete=models.CASCADE)
    per_km_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.config.name} - Additional Price"

class TimeMultiplierSlab(models.Model):
    config = models.ForeignKey(PricingConfig, related_name="tmfs", on_delete=models.CASCADE)
    from_minutes = models.PositiveIntegerField()
    to_minutes = models.PositiveIntegerField()
    multiplier = models.FloatField()

    class Meta:
        unique_together = ("config", "from_minutes", "to_minutes")

    def __str__(self):
        return f"{self.config.name} - {self.from_minutes}-{self.to_minutes} min"

class WaitingCharge(models.Model):
    config = models.ForeignKey(PricingConfig, related_name="wcs", on_delete=models.CASCADE)
    free_minutes = models.PositiveIntegerField(default=0)
    charge_per_slab = models.DecimalField(max_digits=10, decimal_places=2)
    slab_minutes = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.config.name} - Waiting Charge"

class ConfigChangeLog(models.Model):
    ACTION_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
    ]
    config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(choices=ACTION_CHOICES, max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.config.name} - {self.action} by {self.user} at {self.timestamp}"
