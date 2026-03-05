from django.db import migrations


PREDEFINED_PARTS = [
    ("Brake Liner", "120.00"),
    ("Coupling", "150.00"),
    ("Plate Bolt", "80.00"),
    ("Half Axle", "200.00"),
    ("Wheel Bearing", "180.00"),
]


def create_predefined_parts(apps, schema_editor):
    SparePart = apps.get_model("billing", "SparePart")
    for name, price in PREDEFINED_PARTS:
        SparePart.objects.get_or_create(name=name, defaults={"default_price": price, "is_active": True})


def remove_predefined_parts(apps, schema_editor):
    SparePart = apps.get_model("billing", "SparePart")
    SparePart.objects.filter(name__in=[n for n, _ in PREDEFINED_PARTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0002_sparepart_servicebillpart"),
    ]

    operations = [
        migrations.RunPython(create_predefined_parts, remove_predefined_parts),
    ]
