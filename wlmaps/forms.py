#!/usr/bin/env python -tt
# encoding: utf-8

import json
from subprocess import check_call, CalledProcessError

from django import forms
from django.forms import ModelForm
from django.core.files.storage import default_storage

from settings import MEDIA_ROOT
from wlmaps.models import Map
import os
from settings import WIDELANDS_SVN_DIR

class UploadMapForm(ModelForm):
    """
    We have to handle here three different kind of files:
    1. The map which is uploaded
    2. The files created by 'wl_map_info'
        a. The json file containing infos of the map
        b. The image of the minimap (png)

    The filename of uploaded maps may contain bad characters which must be handled.

    If a map get deleted in the database, the underlying files (.wmf, .png) still exists. Uploading
    a map with the same name does not overwrite the existing file(s), instead they get a
    name in form of 'filename_<random_chars>.wmf(.png)'. This is importand for linking the correct
    minimap.
    The map file and the minimap (png) have different random characters in such a case, because the map
    get saved twice: One time for the call to wl_map_info, and when the model is saved.
    """

    class Meta:
        model = Map
        fields = ['file', 'uploader_comment']

    def clean(self):
        cleaned_data = super(UploadMapForm, self).clean()

        mem_file_obj = cleaned_data.get('file')
        if not mem_file_obj:
            # no clean file => abort
            return cleaned_data

        try:
            # Try to make a safe filename
            safe_name = default_storage.get_valid_name(mem_file_obj.name)
            file_path = MEDIA_ROOT + 'wlmaps/maps/' + safe_name
            saved_file = default_storage.save(file_path, mem_file_obj)
        except UnicodeEncodeError:
            self._errors['file'] = self.error_class(
                ['The filename contains characters which cannot be handled. Please rename and upload again.'])
            del cleaned_data['file']
            return cleaned_data

        try:
            # call map info tool to generate minimap and json info file
            old_cwd = os.getcwd()
            os.chdir(WIDELANDS_SVN_DIR)
            check_call(['wl_map_info', saved_file])

            # TODO(shevonar): delete file because it will be saved again when
            # the model is saved. File should not be saved twice
            default_storage.delete(saved_file)
            os.chdir(old_cwd)
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

        # mapinfo["minimap"] is an absolute path.
        # We partition it to get the correct file path
        minimap_path = mapinfo['minimap'].partition(MEDIA_ROOT)[2]
        self.instance.minimap = '/' + minimap_path

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
