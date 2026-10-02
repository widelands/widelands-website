def load_related(objects, rel_qs, rel_field_name, cache_field_name=None):
    """Load in one SQL query the objects from query set (rel_qs) which is
    linked to objects from (objects) via the field (rel_field_name)."""

    obj_map = dict((x.id, x) for x in objects)
    rel_field = rel_qs.model._meta.get_field(rel_field_name)
    cache_field_name = f"{rel_qs.model.__name__.lower()}_cache"

    rel_objects = rel_qs.filter(**{f"{rel_field.name}__in": list(obj_map.keys())})

    temp_map = {}
    for rel_obj in rel_objects:
        pk = getattr(rel_obj, rel_field.attname)
        temp_map.setdefault(pk, []).append(rel_obj)

    for pk, rel_list in temp_map.items():
        setattr(obj_map[pk], cache_field_name, rel_list)
