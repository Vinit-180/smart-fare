from datetime import datetime
from decimal import Decimal
from django.db.models import Q
from .models import PricingConfig, DistanceBasePrice, DistanceAdditionalPrice, TimeMultiplierSlab, WaitingCharge

class PricingCalculationError(Exception):
    pass

def calculate_price(ride_date: str, total_distance_km: float, total_ride_time_min: int, waiting_time_min: int):
    """
    Calculates the price breakdown for a ride.
    Returns a dict with breakdown and final price.
    Raises PricingCalculationError if no active config exists or invalid input.
    """
    # Find active config
    try:
        config = PricingConfig.objects.get(is_active=True)
    except PricingConfig.DoesNotExist:
        raise PricingCalculationError("No active pricing configuration found.")

    # Parse date and weekday
    ride_dt = datetime.strptime(ride_date, "%Y-%m-%d")
    weekday = ride_dt.strftime("%A").lower()

    # DBP: Distance Base Price for weekday
    try:
        dbp = DistanceBasePrice.objects.get(config=config, weekday=weekday)
    except DistanceBasePrice.DoesNotExist:
        raise PricingCalculationError(f"No DBP for {weekday} in active config.")

    base_distance = min(total_distance_km, dbp.up_to_kms)
    base_price = Decimal(dbp.price)

    # DAP: Additional distance price
    dap = DistanceAdditionalPrice.objects.filter(config=config).first()
    additional_distance = max(0, total_distance_km - dbp.up_to_kms)
    additional_distance_charge = Decimal(0)
    if dap and additional_distance > 0:
        additional_distance_charge = Decimal(dap.per_km_price) * Decimal(additional_distance)

    # TMF: Time Multiplier
    tmf_slab = TimeMultiplierSlab.objects.filter(
        config=config,
        from_minutes__lte=total_ride_time_min,
        to_minutes__gte=total_ride_time_min
    ).first()
    time_multiplier_charge = Decimal(0)
    if tmf_slab:
        time_multiplier_charge = (base_price + additional_distance_charge) * Decimal(tmf_slab.multiplier)

    # WC: Waiting Charge
    wc = WaitingCharge.objects.filter(config=config).first()
    waiting_charge = Decimal(0)
    if wc and waiting_time_min > wc.free_minutes:
        slabs = (waiting_time_min - wc.free_minutes + wc.slab_minutes - 1) // wc.slab_minutes
        waiting_charge = Decimal(wc.charge_per_slab) * slabs

    # Edge cases
    if total_distance_km <= 0:
        base_price = Decimal(0)
        additional_distance_charge = Decimal(0)
    if total_ride_time_min <= 0:
        time_multiplier_charge = Decimal(0)
    if waiting_time_min <= 0:
        waiting_charge = Decimal(0)

    final_price = base_price + additional_distance_charge + time_multiplier_charge + waiting_charge

    return {
        "base_price": float(base_price),
        "additional_distance_charge": float(additional_distance_charge),
        "time_multiplier_charge": float(time_multiplier_charge),
        "waiting_charge": float(waiting_charge),
        "final_price": float(final_price),
    }
