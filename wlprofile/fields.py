from StringIO import StringIO
from django.db import models
import logging


class ExtendedImageField(models.ImageField):
    """
    Extended ImageField that can resize image before saving it.
    """
    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        super(ExtendedImageField, self).__init__(*args, **kwargs)


    def save_form_data(self, instance, data):
        if data is not None and data != self.default:
            if not data:
                data = self.default
                if instance.avatar != self.default:
                        instance.avatar.delete()
            else:
                if hasattr(data, 'read') and self.width and self.height:
                    content = self.resize_image(data.read(), width=self.width, height=self.height)
                    data = SimpleUploadedFile(instance.user.username + ".png", content, "image/png")
            super(ExtendedImageField, self).save_form_data(instance, data)


    def resize_image(self, rawdata, width, height):
        """
        Resize image to fit it into (width, height) box.
        """
        from PIL import Image

        image = Image.open(StringIO(rawdata))
        try:
            oldw, oldh = image.size

            if oldw > width or oldh > height:
                if oldw >= oldh:
                    x = int(round((oldw - oldh) / 2.0))
                    image = image.crop((x, 0, (x + oldh) - 1, oldh - 1))
                else:
                    y = int(round((oldh - oldw) / 2.0))
                    image = image.crop((0, y, oldw - 1, (y + oldw) - 1))
                image = image.resize((width, height), resample=Image.ANTIALIAS)
        except Exception, err:
            logging.error(err)
            return ''

        string = StringIO()
        image.save(string, format='PNG')
        return string.getvalue()
