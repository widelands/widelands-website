# Generated by Django 2.2.28 on 2022-12-15 09:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wlprofile", "0003_auto_20221130_1732"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="time_zone",
            field=models.FloatField(
                choices=[
                    (-12.0, "UTC -12"),
                    (-11.0, "UTC -11"),
                    (-10.0, "UTC -10"),
                    (-9.5, "UTC -09.5"),
                    (-9.0, "UTC -09"),
                    (-8.5, "UTC -08.5"),
                    (-8.0, "UTC -08"),
                    (-7.0, "UTC -07"),
                    (-6.0, "UTC -06"),
                    (-5.0, "UTC -05"),
                    (-4.0, "UTC -04"),
                    (-3.5, "UTC -03.5"),
                    (-3.0, "UTC -03"),
                    (-2.0, "UTC -02"),
                    (-1.0, "UTC -01"),
                    (0.0, "UTC"),
                    (1.0, "UTC +01"),
                    (2.0, "UTC +02"),
                    (3.0, "UTC +03"),
                    (3.5, "UTC +03.5"),
                    (4.0, "UTC +04"),
                    (4.5, "UTC +04.5"),
                    (5.0, "UTC +05"),
                    (5.5, "UTC +05.5"),
                    (5.75, "UTC +05.45"),
                    (6.0, "UTC +06"),
                    (6.5, "UTC +06.5"),
                    (7.0, "UTC +07"),
                    (8.0, "UTC +08"),
                    (9.0, "UTC +09"),
                    (9.5, "UTC +09.5"),
                    (10.0, "UTC +10"),
                    (10.5, "UTC +10.5"),
                    (11.0, "UTC +11"),
                    (11.5, "UTC +11.5"),
                    (12.0, "UTC +12"),
                    (12.75, "UTC +12.75"),
                    (13.0, "UTC +13"),
                    (14.0, "UTC +14"),
                ],
                default=0.0,
                verbose_name="Time zone",
            ),
        ),
    ]
