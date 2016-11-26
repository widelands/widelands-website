from django import forms
from models import Image

import os

class UploadImageForm(forms.Form):
    imagename = forms.ImageField(max_length=100)

    def clean_imagename( self ):
        in_mem_img = self.cleaned_data["imagename"]
        
        if Image.objects.has_image(in_mem_img.name):
            img = Image.objects.get(name = in_mem_img.name)
            raise forms.ValidationError(
                ("An Image with name '%(name)s' is already attached to %(object)s '%(obj_name)s'. \
                 Use the existing one or rename your file and upload gain."),
                params={'name': img.name, 'object': img.content_type, 'obj_name': img.content_object}
                )

