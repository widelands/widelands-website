# django_messages (vendored)

User-to-user private messages. This is a vendored copy of
[django-messages](https://github.com/arneb/django-messages) by Arne Brodowski
and contributors (see `AUTHORS`), taken from the fork by frankystone at
https://github.com/frankystone/django-messages, commit
`8f6605be2e4f4c05817ed9922c0011aaedf18f57` ("made it django4 compatible",
2024-12-16). It is distributed under the BSD license in `LICENSE`.

The app label (`django_messages`), the `Message` model, its table and the
migrations are unchanged, so existing databases keep working. Site-specific
extensions live in `django_messages_wl`, and the templates in
`templates/django_messages/`.

## Local modifications

- Removed what the site does not use: the bundled templates (all overridden
  in `templates/django_messages/`), the pinax notification templates and
  hooks, the translations (`USE_I18N = False`), the `inbox_count` template
  tag, `format_subject()`, the unused `management.py` and
  `delete_deleted_messages` command, `signals.py`, the upstream tests, the
  docs and the packaging files.
- Removed compatibility code for old Django versions and the django-mailer
  fallback; uses `django.contrib.auth.get_user_model()` directly.
- Reformatted with black.
- `delete` and `undelete` accept only POST requests, and the `next`
  redirect of `delete`, `undelete` and `compose` must point to this site.
