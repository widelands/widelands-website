from django.db import migrations

# Rows that can never have been set deliberately: the empty string, and
# base64(sha1("")), which the old GGZAuth.save() wrote for auto-created rows.
BAD_PASSWORDS = ["", "2jmj7l5rSw0yVb/vlWAYkK/YBwk="]


def delete_empty_passwords(apps, schema_editor):
    GGZAuth = apps.get_model("wlggz", "GGZAuth")
    GGZAuth.objects.filter(password__in=BAD_PASSWORDS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("wlggz", "0002_auto_20160805_2004"),
    ]

    operations = [
        migrations.RunPython(delete_empty_passwords, migrations.RunPython.noop),
    ]
