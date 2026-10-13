# ============================================================
# TARIFF CONFIGURATIONS
# ============================================================

BATTERY_STARTER = {
    "name": "Origin Battery Starter",

    "peak_import_rate": 0.3289,
    "off_peak_import_rate": 0.2849,

    "peak_export_rate": 0.28,
    "off_peak_export_rate": 0.03,

    "peak_start_hour": 16.0,
    "peak_end_hour": 21.0,
}


BATTERY_LITE = {
    "name": "Origin Battery Lite",

    "peak_import_rate": 0.3289,
    "off_peak_import_rate": 0.2849,

    "peak_export_rate": 0.28,
    "off_peak_export_rate": 0.03,

    "peak_start_hour": 16.0,
    "peak_end_hour": 21.0,

    "event_export_rate": 1.00,
}

BATTERY_CHARGE = {
    "name": "Origin Battery Charge",

    "peak_import_rate": 0.4361,
    "overnight_import_rate": 0.3121,
    "shoulder_import_rate": 0.2827,

    "free_period_rate": 0.0,
    "free_period_start_hour": 11.0,
    "free_period_end_hour": 15.0,
    "free_period_daily_limit_kwh": 28.0,
    "free_period_excess_rate": 0.3121,

    "peak_export_rate": 0.11,
    "peak_export_start_hour": 18.0,
    "peak_export_end_hour": 21.0,
    "peak_export_daily_limit_kwh": 10.0,
}