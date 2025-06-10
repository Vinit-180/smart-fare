from django.contrib import admin
from .models import (
    PricingConfig,
    DistanceBasePrice,
    DistanceAdditionalPrice,
    TimeMultiplierSlab,
    WaitingCharge,
    ConfigChangeLog,
)

from django import forms
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import ConfigChangeLog

class DistanceBasePriceInline(admin.TabularInline):
    model = DistanceBasePrice
    extra = 1

class DistanceAdditionalPriceInline(admin.TabularInline):
    model = DistanceAdditionalPrice
    extra = 1

class TimeMultiplierSlabInline(admin.TabularInline):
    model = TimeMultiplierSlab
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        class CleanedFormSet(formset):
            def clean(inner_self):
                super().clean()
                seen = []
                for form in inner_self.forms:
                    if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                        continue
                    from_min = form.cleaned_data['from_minutes']
                    to_min = form.cleaned_data['to_minutes']
                    for f, t in seen:
                        if max(f, from_min) < min(t, to_min):
                            raise forms.ValidationError("Overlapping time slabs detected.")
                    seen.append((from_min, to_min))
        return CleanedFormSet

class WaitingChargeInline(admin.TabularInline):
    model = WaitingCharge
    extra = 1

class PricingConfigAdmin(admin.ModelAdmin):
    inlines = [DistanceBasePriceInline, DistanceAdditionalPriceInline, TimeMultiplierSlabInline, WaitingChargeInline]
    list_display = ("name", "is_active", "created_by", "created_at")
    actions = ["make_active"]

    def save_model(self, request, obj, form, change):
        # Enforce only one active config
        if obj.is_active:
            PricingConfig.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)
        action = "updated" if change else "created"
        ConfigChangeLog.objects.create(
            config=obj, user=request.user, action=action,
            details=f"Config {action} via admin by {request.user}"
        )

    def delete_model(self, request, obj):
        ConfigChangeLog.objects.create(
            config=obj, user=request.user, action="deleted",
            details=f"Config deleted via admin by {request.user}"
        )
        super().delete_model(request, obj)

    def make_active(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one config to activate.", level=messages.ERROR)
            return
        config = queryset.first()
        PricingConfig.objects.exclude(pk=config.pk).update(is_active=False)
        config.is_active = True
        config.save()
        self.message_user(request, f"{config.name} is now the active config.")
    make_active.short_description = "Set selected config as active"

admin.site.register(PricingConfig, PricingConfigAdmin)

class ConfigChangeLogAdmin(admin.ModelAdmin):
    list_display = ("config", "user", "action", "timestamp", "details")
    list_filter = ("config", "action", "user")
    search_fields = ("details",)

admin.site.register(ConfigChangeLog, ConfigChangeLogAdmin)
