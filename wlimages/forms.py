from django import forms
from models import Image

import os

class UploadImageForm(forms.Form):
    # max_length = 90 because the length of 'upload_to =' has to be considered
    imagename = forms.ImageField(max_length=90)

    def clean_imagename( self ):
        in_mem_img = self.cleaned_data["imagename"]
        
        if Image.objects.has_image(in_mem_img.name):
            # Get the existing image to show it's properties
            exist_img = Image.objects.get(name = in_mem_img.name)
            raise forms.ValidationError(
                ("An Image with name '%(name)s' is already attached to %(object)s '%(obj_name)s'. \
                 Use the existing one or rename your file and upload gain."),
                params={'name': exist_img.name, 'object': exist_img.content_type, 'obj_name': exist_img.content_object}
                )

