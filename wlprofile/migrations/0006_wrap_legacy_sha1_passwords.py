from django.db import migrations

from wlprofile.hashers import wrap_legacy_sha1_hashes


def wrap_sha1_passwords(apps, schema_editor):
    wrap_legacy_sha1_hashes(apps.get_model("auth", "User"))


class Migration(migrations.Migration):

    dependencies = [
        ("wlprofile", "0005_alter_profile_time_display"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(wrap_sha1_passwords, migrations.RunPython.noop),
    ]
