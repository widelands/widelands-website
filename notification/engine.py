import sys
import time
import logging
import traceback
import base64

try:
    import pickle as pickle
except ImportError:
    import pickle

from django.conf import settings
from django.core.mail import mail_admins
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from .lockfile import FileLock, AlreadyLocked, LockTimeout

from notification.models import NoticeQueueBatch
from notification import models as notification

# lock timeout value. how long to wait for the lock to become available.
# default behavior is to never wait for the lock to be available.
LOCK_WAIT_TIMEOUT = getattr(settings, "NOTIFICATION_LOCK_WAIT_TIMEOUT", -1)


def send_all():
    lock = FileLock("send_notices")

    logging.debug("acquiring lock...")
    try:
        lock.acquire(LOCK_WAIT_TIMEOUT)
    except AlreadyLocked:
        logging.debug("lock already in place. quitting.")
        return
    except LockTimeout:
        logging.debug("waiting for the lock timed out. quitting.")
        return
    logging.debug("acquired.")

    batches, sent = 0, 0
    start_time = time.time()

    try:
        for queued_batch in NoticeQueueBatch.objects.all():
            notices = pickle.loads(base64.b64decode(queued_batch.pickled_data))
            try:
                for user, label, extra_context, on_site in notices:
                    user = User.objects.get(pk=user)
                    logging.info('emitting notice to %s' % user)

                    # call this once per user to be atomic and allow for logging to
                    # accurately show how long each takes.
                    notification.send_now([user], label, extra_context, on_site)
                    sent += 1
            except User.DoesNotExist:
                # There might be a notice addressing a meanwhile deleted User
                pass
            queued_batch.delete()
            batches += 1
    except:
        # get the exception
        _, e, t = sys.exc_info()
        # email admins
        current_site = Site.objects.get_current()
        subject = f"{current_site.name} emit_notices: {e}"
        message = f"Traceback in engine.py:\n{traceback.format_tb(t)}"
        mail_admins(subject, message, fail_silently=True)
        # log it as critical
        logging.critical(f"an exception occurred: {e}, {traceback.format_tb(t)}")
    finally:
        logging.debug("releasing lock...")
        lock.release()
        logging.debug("released.")

    logging.info("")
    logging.info(f"{batches} batches, {sent} sent")
    logging.info(f"done in {time.time() - start_time:.2f} seconds")
