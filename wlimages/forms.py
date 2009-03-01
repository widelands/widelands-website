from django import forms
from models import Image

import os

class UploadImageForm(forms.Form):
    image = forms.ImageField()
     
    def clean_image( self ):
        image = self.cleaned_data["image"]

        if Image.objects.has_image(image.name.lower()):
            raise forms.ValidationError, "An Image with this name already exists. Please rename and upload again."


