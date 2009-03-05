from django import forms
from models import Image

import os

class UploadImageForm(forms.Form):
    imagename = forms.ImageField()
     
    def clean_imagename( self ):
        print "self:", self

        name = self.cleaned_data["imagename"]

        if Image.objects.has_image(name.name.lower()):
            raise forms.ValidationError, "An Image with this name already exists. Please rename and upload again."


