from django.conf import settings
from anti_spam.models import FoundSpam
import re


def check_for_spam(*args, **kwargs):

    is_spam = check_text(kwargs['text_to_check'])

    if is_spam:
        fs = FoundSpam(content_object=kwargs['instance'],
                       user=kwargs['user'],
                       spam_text=kwargs['text_to_check'][:100])
        fs.save()
    return is_spam


def check_text(text):
    if any(x in text.lower() for x in settings.ANTI_SPAM_KWRDS):
        return True
    if re.search(settings.ANTI_SPAM_PHONE_NR, text):
        return True
    return False
