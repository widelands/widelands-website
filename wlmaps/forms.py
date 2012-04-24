#!/usr/bin/env python -tt
# encoding: utf-8

import Image
from cStringIO import StringIO

from django import forms
from django.forms import ModelForm, ValidationError

from settings import WIDELANDS_SVN_DIR, MEDIA_ROOT

from wlmaps.models import Map
from widelandslib.map import WidelandsMap, WlMapLibraryException


class UploadMapForm(ModelForm):
    class Meta:
        model = Map
        fields = ['file', 'uploader_comment']


    def clean(self):
        cleaned_data = super(UploadMapForm, self).clean()

        file = cleaned_data.get('file')
        if not file:
            # no clean file => abort
            return cleaned_data

        mapdata = file.read()
        wlmap = WidelandsMap()
        try:
            wlmap.load(StringIO(mapdata))
        except WlMapLibraryException:
            raise forms.ValidationError("The map file is invalid.")

        if Map.objects.filter(name = wlmap.name):
            raise forms.ValidationError("Map with the same name already exists.")

        cleaned_data['file'].name = "%s/wlmaps/maps/%s.wmf" % (MEDIA_ROOT, wlmap.name)

        # Create the minimap
        minimap = wlmap.make_minimap(WIDELANDS_SVN_DIR)
        minimap_path = "%s/wlmaps/minimaps/%s.png" % (MEDIA_ROOT, wlmap.name)
        minimap_url = "/wlmaps/minimaps/%s.png" % wlmap.name
        minimap_image = Image.fromarray(minimap)
        minimap_image.save(minimap_path)
        # TODO: handle filesystem errors

        # Add information to the map
        self.instance.name = wlmap.name
        self.instance.author = wlmap.author
        self.instance.w = wlmap.w
        self.instance.h = wlmap.h
        self.instance.nr_players = wlmap.nr_players
        self.instance.descr = wlmap.descr
        self.instance.minimap = minimap_url
        self.instance.world_name = wlmap.world_name

        return cleaned_data


    def save(self, *args, **kwargs):
        map = super(UploadMapForm, self).save(*args, **kwargs)
        if not kwargs['commit'] == False:
            map.save()
        return map
