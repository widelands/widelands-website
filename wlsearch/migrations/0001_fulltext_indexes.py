from django.db import migrations

# The FULLTEXT indexes searched by wlsearch.views. Only MariaDB/MySQL has
# them; other databases search without an index.
FULLTEXT_INDEXES = {
    ("pybb", "Post"): ["body_text"],
    ("pybb", "Topic"): ["name"],
    ("wiki", "Article"): ["title", "content", "summary"],
    ("news", "Post"): ["title", "body"],
    ("wlmaps", "Map"): ["name", "author", "descr", "uploader_comment"],
}


def _indexes(apps, schema_editor):
    quote = schema_editor.quote_name
    for (app_label, model_name), columns in FULLTEXT_INDEXES.items():
        table = apps.get_model(app_label, model_name)._meta.db_table
        yield quote(table), quote(f"{table}_fulltext"), ", ".join(map(quote, columns))


def add_fulltext_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return
    for table, index, columns in _indexes(apps, schema_editor):
        schema_editor.execute(
            f"ALTER TABLE {table} ADD FULLTEXT INDEX {index} ({columns})"
        )


def remove_fulltext_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return
    for table, index, _ in _indexes(apps, schema_editor):
        schema_editor.execute(f"ALTER TABLE {table} DROP INDEX {index}")


class Migration(migrations.Migration):
    # MariaDB cannot roll back DDL statements
    atomic = False

    dependencies = [
        ("news", "0001_squashed_0004_remove_post_tags"),
        ("pybb", "0007_reaction"),
        ("wiki", "0007_remove_article_markup_remove_changeset_old_markup"),
        ("wlmaps", "0004_auto_20210201_1547"),
    ]

    operations = [
        migrations.RunPython(add_fulltext_indexes, remove_fulltext_indexes),
    ]
