#!/usr/bin/env python -tt
# encoding: utf-8

import json
from subprocess import check_call, CalledProcessError

from django import forms
from django.forms import ModelForm
from django.core.files.storage import default_storage

from settings import MEDIA_ROOT
from wlmaps.models import Map


class UploadMapForm(ModelForm):

    class Meta:
        model = Map
        fields = ['file', 'uploader_comment']

    def clean(self):
        cleaned_data = super(UploadMapForm, self).clean()

        mem_file_obj = cleaned_data.get('file')
        if not mem_file_obj:
            # no clean file => abort
            return cleaned_data

        file_path = MEDIA_ROOT + 'wlmaps/maps/' + default_storage.get_valid_name(mem_file_obj.name)
        saved_file = default_storage.save(file_path, mem_file_obj)
        try:
            # call map info tool to generate minimap and json info file
            check_call(['wl_map_info', saved_file])
            # TODO(shevonar): delete file because it will be saved again when
            # the model is saved. File should not be saved twice
            default_storage.delete(saved_file)
        except CalledProcessError:
            self._errors['file'] = self.error_class(
                ['The map file could not be processed.'])
            del cleaned_data['file']
            return cleaned_data

        mapinfo = json.load(open(saved_file + '.json'))

        if Map.objects.filter(name=mapinfo['name']):
            self._errors['file'] = self.error_class(
                ['A map with the same name already exists.'])
            del cleaned_data['file']
            return cleaned_data

        # Add information to the map
        self.instance.name = mapinfo['name']
        self.instance.author = mapinfo['author']
        self.instance.w = mapinfo['width']
        self.instance.h = mapinfo['height']
        self.instance.nr_players = mapinfo['nr_players']
        self.instance.descr = mapinfo['description']
        self.instance.hint = mapinfo['hint']

        self.instance.world_name = mapinfo['world_name']
        # mapinfo["minimap"] is an absolute path and cannot be used.
        self.instance.minimap = '/wlmaps/maps/' + default_storage.get_valid_name(mem_file_obj.name) + '.png'

        # the json file is no longer needed
        default_storage.delete(saved_file + '.json')
        
        return cleaned_data

    def save(self, *args, **kwargs):
        map = super(UploadMapForm, self).save(*args, **kwargs)
        if kwargs['commit']:
            map.save()
        return map


class EditCommentForm(ModelForm):

    class Meta:
        model = Map
        fields = ['uploader_comment', ]
