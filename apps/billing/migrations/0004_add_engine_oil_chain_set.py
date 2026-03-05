from django.db import migrations


NEW_PARTS = [
    ("Engine Oil", "350.00"),
    ("Chain Set", "750.00"),
]


def add_new_parts(apps, schema_editor):
    SparePart = apps.get_model("billing", "SparePart")
    for name, price in NEW_PARTS:
        SparePart.objects.get_or_create(name=name, defaults={"default_price": price, "is_active": True})


def remove_new_parts(apps, schema_editor):
    SparePart = apps.get_model("billing", "SparePart")
    SparePart.objects.filter(name__in=[n for n, _ in NEW_PARTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0003_seed_spare_parts"),
    ]

    operations = [
        migrations.RunPython(add_new_parts, remove_new_parts),
    ]
