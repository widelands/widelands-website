_GGZPERMS2PERMS = {
      7: "REGISTERED",
    127: "SUPERUSER",
}
# TODO
# import os
# os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
# import sys
# sys.path.append("..")
# from django.contrib.auth.models import User
# from wlggz.models import GGZAuth

#
            try:
                djuser = User.objects.get(username=self._name)
                perm = GGZAuth.objects.get(user=djuser)
                cor_digest = base64.standard_b64decode(perm.password)
                given_digest = hashlib.sha1(_string(p)).digest()
                password_ok = cor_digest == given_digest
                print "cor_digest: %r, given_digest: %r" % (cor_digest, given_digest)

                self._permissions = self._GGZPERMS2PERMS[perm.permissions]
            except (User.DoesNotExist, GGZAuth.DoesNotExist) as e:
                print "e: %r" % (e)
                password_ok = False


