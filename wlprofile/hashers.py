"""Support for legacy SHA1 password hashes.

Django 5.1 removed SHA1PasswordHasher. Old accounts still store
``sha1$<salt>$<hexdigest>`` hashes; migration 0006 rewraps them as
``pbkdf2_wrapped_sha1$<iterations>$<salt>$<pbkdf2(hexdigest)>`` so they stay
usable and are no longer weak at rest. Django rehashes them with the default
hasher on the user's next successful login.

See https://docs.djangoproject.com/en/5.2/topics/auth/passwords/#password-upgrading-without-requiring-a-login
"""

import hashlib

from django.contrib.auth.hashers import PBKDF2PasswordHasher

LEGACY_SHA1_PREFIX = "sha1$"


class PBKDF2WrappedSHA1PasswordHasher(PBKDF2PasswordHasher):
    algorithm = "pbkdf2_wrapped_sha1"

    def encode_sha1_hash(self, sha1_hash, salt, iterations=None):
        return super().encode(sha1_hash, salt, iterations)

    def encode(self, password, salt, iterations=None):
        # Same digest the removed SHA1PasswordHasher produced.
        sha1_hash = hashlib.sha1((salt + password).encode()).hexdigest()
        return self.encode_sha1_hash(sha1_hash, salt, iterations)


def wrap_legacy_sha1_hashes(user_model):
    """Rewrap every ``sha1$`` password of ``user_model`` in PBKDF2."""
    hasher = PBKDF2WrappedSHA1PasswordHasher()
    users = user_model.objects.filter(password__startswith=LEGACY_SHA1_PREFIX)
    for user in users.only("pk", "password").iterator():
        _, salt, sha1_hash = user.password.split("$", 2)
        user.password = hasher.encode_sha1_hash(sha1_hash, salt)
        user.save(update_fields=["password"])
