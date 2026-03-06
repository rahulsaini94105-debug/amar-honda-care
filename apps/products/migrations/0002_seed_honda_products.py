from django.db import migrations


CATEGORIES = [
    "Engine Parts",
    "Brake Parts",
    "Transmission Parts",
    "Electrical Parts",
    "Body Parts",
    "Lubricants & Oils",
    "Chain & Drive Parts",
    "Wheel & Bearing Parts",
]

PRODUCTS = [
    # (name, category, selling_price, purchase_price, stock_qty, low_stock_limit, unit)
    # Engine Parts
    ("Piston Ring Set",      "Engine Parts",         350.00, 250.00, 20, 5, "Set"),
    ("Engine Gasket Kit",    "Engine Parts",         450.00, 320.00, 15, 5, "Set"),
    ("Valve Set",            "Engine Parts",         280.00, 200.00, 10, 3, "Set"),
    ("Carburetor Jet",       "Engine Parts",         120.00,  80.00, 25, 5, "Pcs"),
    ("Air Filter",           "Engine Parts",          80.00,  50.00, 30, 8, "Pcs"),
    ("Spark Plug",           "Engine Parts",          60.00,  35.00, 50, 10, "Pcs"),
    ("Engine Oil Filter",    "Engine Parts",          90.00,  60.00, 25, 5, "Pcs"),

    # Lubricants & Oils
    ("Engine Oil (1L)",      "Lubricants & Oils",    350.00, 270.00, 40, 10, "Ltr"),
    ("Gear Oil",             "Lubricants & Oils",    180.00, 130.00, 20,  5, "Ltr"),
    ("Brake Oil",            "Lubricants & Oils",    120.00,  85.00, 20,  5, "Btl"),

    # Brake Parts
    ("Brake Liner",          "Brake Parts",          120.00,  80.00, 30, 8, "Pcs"),
    ("Brake Shoe Set",       "Brake Parts",          200.00, 140.00, 15, 5, "Set"),
    ("Brake Cable",          "Brake Parts",          150.00, 100.00, 20, 5, "Pcs"),
    ("Brake Drum",           "Brake Parts",          350.00, 250.00, 10, 3, "Pcs"),
    ("Brake Plate",          "Brake Parts",           80.00,  55.00, 15, 5, "Pcs"),

    # Transmission Parts
    ("Coupling",             "Transmission Parts",   150.00, 100.00, 20, 5, "Pcs"),
    ("Plate Bolt",           "Transmission Parts",    80.00,  50.00, 40, 8, "Pcs"),
    ("Clutch Plate Set",     "Transmission Parts",   400.00, 280.00, 10, 3, "Set"),
    ("Clutch Cable",         "Transmission Parts",   180.00, 120.00, 15, 5, "Pcs"),

    # Chain & Drive Parts
    ("Chain Set",            "Chain & Drive Parts",  750.00, 550.00, 10, 3, "Set"),
    ("Chain Sprocket",       "Chain & Drive Parts",  300.00, 210.00, 10, 3, "Pcs"),
    ("Chain Link",           "Chain & Drive Parts",   50.00,  30.00, 50, 10, "Pcs"),

    # Wheel & Bearing Parts
    ("Half Axle",            "Wheel & Bearing Parts", 200.00, 140.00, 15, 5, "Pcs"),
    ("Wheel Bearing",        "Wheel & Bearing Parts", 180.00, 120.00, 20, 5, "Pcs"),
    ("Front Fork Oil Seal",  "Wheel & Bearing Parts", 120.00,  80.00, 20, 5, "Set"),
    ("Tyre Tube Front",      "Wheel & Bearing Parts", 150.00, 110.00, 20, 5, "Pcs"),
    ("Tyre Tube Rear",       "Wheel & Bearing Parts", 180.00, 130.00, 20, 5, "Pcs"),

    # Electrical Parts
    ("Headlight Bulb",       "Electrical Parts",      60.00,  35.00, 40, 10, "Pcs"),
    ("Indicator Bulb",       "Electrical Parts",      20.00,  12.00, 60, 10, "Pcs"),
    ("Battery (12V)",        "Electrical Parts",     850.00, 650.00,  8,  3, "Pcs"),
    ("Rectifier",            "Electrical Parts",     350.00, 250.00, 10,  3, "Pcs"),
    ("CDI Unit",             "Electrical Parts",     450.00, 320.00,  8,  3, "Pcs"),
    ("Self Start Motor",     "Electrical Parts",     600.00, 450.00,  5,  2, "Pcs"),

    # Body Parts
    ("Side Panel Left",      "Body Parts",           250.00, 180.00, 10, 3, "Pcs"),
    ("Side Panel Right",     "Body Parts",           250.00, 180.00, 10, 3, "Pcs"),
    ("Rear Fender",          "Body Parts",           300.00, 210.00,  8, 3, "Pcs"),
    ("Muffler / Silencer",   "Body Parts",           800.00, 600.00,  5, 2, "Pcs"),
    ("Handle Grip Set",      "Body Parts",            80.00,  50.00, 20, 5, "Set"),
    ("Footrest Set",         "Body Parts",           150.00, 100.00, 10, 3, "Set"),
    ("Mirror Left",          "Body Parts",            90.00,  60.00, 15, 5, "Pcs"),
    ("Mirror Right",         "Body Parts",            90.00,  60.00, 15, 5, "Pcs"),
]


def seed_products(apps, schema_editor):
    Category = apps.get_model("products", "Category")
    Product = apps.get_model("products", "Product")

    # Create categories
    cat_map = {}
    for cat_name in CATEGORIES:
        cat, _ = Category.objects.get_or_create(name=cat_name)
        cat_map[cat_name] = cat

    # Create products
    for name, cat_name, sell_price, buy_price, stock, low_limit, unit in PRODUCTS:
        Product.objects.get_or_create(
            name=name,
            defaults={
                "category": cat_map[cat_name],
                "selling_price": sell_price,
                "purchase_price": buy_price,
                "stock_qty": stock,
                "low_stock_limit": low_limit,
                "unit": unit,
                "is_active": True,
            }
        )


def remove_seeded_products(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    Category = apps.get_model("products", "Category")
    product_names = [p[0] for p in PRODUCTS]
    Product.objects.filter(name__in=product_names).delete()
    Category.objects.filter(name__in=CATEGORIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_products, remove_seeded_products),
    ]
