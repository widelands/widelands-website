from io import BytesIO
from django.db import models
import logging
from django.core.files.uploadedfile import SimpleUploadedFile

# Larger images are rejected, decoding them would need too much memory
MAX_IMAGE_PIXELS = 4096 * 4096


class ExtendedImageField(models.ImageField):
    """Extended ImageField that can resize image before saving it."""

    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop("width", None)
        self.height = kwargs.pop("height", None)
        super(ExtendedImageField, self).__init__(*args, **kwargs)

    def save_form_data(self, instance, data):
        if data is not None and data != self.default:
            if not data:
                data = self.default
                if instance.avatar != self.default:
                    instance.avatar.delete()
            else:
                if hasattr(data, "read") and self.width and self.height:
                    content = self.resize_image(
                        data.read(), width=self.width, height=self.height
                    )
                    data = SimpleUploadedFile(
                        instance.user.username + ".png", content, "image/png"
                    )
            super(ExtendedImageField, self).save_form_data(instance, data)

    def resize_image(self, rawdata, width, height):
        """Resize image to fit it into (width, height) box."""
        from PIL import Image, ImageOps

        image = Image.open(BytesIO(rawdata))
        try:
            oldw, oldh = image.size

            if oldw > width or oldh > height:
                # Let JPEGs decode at a reduced scale, then crop the centered
                # square and resize it in one pass
                image.draft(None, (width, height))
                image = ImageOps.fit(
                    image, (width, height), method=Image.Resampling.LANCZOS
                )
        except Exception as err:
            logging.error(err)
            return ""

        string = BytesIO()
        image.save(string, format="PNG")
        return string.getvalue()
