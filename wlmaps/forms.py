#!/usr/bin/env python -tt
# encoding: utf-8

import json
from subprocess import check_call, CalledProcessError

from django import forms
from django.forms import ModelForm
from django.conf import settings
from django.core.files.storage import default_storage

from wlmaps.models import Map
import os
import shutil
import tempfile


class UploadMapForm(ModelForm):
    """
    All file operations are done in the temp folder.

    We have to handle here three different kind of files:
    1. The map which is uploaded, stored as e.g '/tmp/tmp_xyz.upload'.
       Because 'wl_map_info' can't handle files with this extension and
       produces a minimap with the same name like the initial name, the
       uploade file will be copied to a file with the name of the
       uploaded file and extension, e.g. '/tmp/original_filename.wmf'
    2. 'wl_map_info' produces two files which will be stored at the same
        location as the uploaded file and named like the map file:
        a. '/tmp/original_filename.wmf.json': Contains infos of the map
        b. '/tmp/original_filename.wmf.png': The image of the minimap (png).

    Because we can't be sure the original filename is a valid filename, we
    may modify it to be a valid filename.
    """

    class Meta:
        model = Map
        fields = ["file", "uploader_comment"]

    def clean(self):
        cleaned_data = super(UploadMapForm, self).clean()

        file_obj = cleaned_data.get("file")
        if not file_obj:
            # no clean file => abort
            return cleaned_data

        # Make a save filename and copy the uploaded file
        saved_file = file_obj.temporary_file_path()
        safe_name = default_storage.get_valid_name(file_obj.name)
        tmpdir = tempfile.gettempdir()
        copied_file = shutil.copyfile(saved_file, os.path.join(tmpdir, safe_name))

        try:
            # call map info tool to generate minimap and json info file
            # change working directory so that the datadir is found
            old_cwd = os.getcwd()
            os.chdir(settings.WIDELANDS_SVN_DIR)
            check_call(["wl_map_info", copied_file])
            os.chdir(old_cwd)
        except CalledProcessError:
            self._errors["file"] = self.error_class(
                ["The map file could not be processed."]
            )
            del cleaned_data["file"]
            os.remove(copied_file)
            return cleaned_data

        mapinfo = json.load(open(copied_file + ".json"))

        if Map.objects.filter(name=mapinfo["name"]):
            self._errors["file"] = self.error_class(
                ["A map with the same name already exists."]
            )
            del cleaned_data["file"]
            # Delete the file copy and the generated files
            try:
                os.remove(copied_file)
                os.remove(copied_file + ".json")
                os.remove(copied_file + ".png")
            except os.FileNotFoundError:
                pass

            return cleaned_data

        # Add information to the map
        self.instance.name = mapinfo["name"]
        self.instance.author = mapinfo["author"]
        self.instance.w = mapinfo["width"]
        self.instance.h = mapinfo["height"]
        self.instance.nr_players = mapinfo["nr_players"]
        self.instance.descr = mapinfo["description"]
        self.instance.hint = mapinfo["hint"]
        self.instance.world_name = mapinfo["world_name"]
        # The field is called 'wl_version_after' even though it actually means the
        # _minimum_ WL version required to play the map for historical reasons
        if "minimum_required_widelands_version" in mapinfo:
            self.instance.wl_version_after = mapinfo[
                "minimum_required_widelands_version"
            ]
        else:
            self.instance.wl_version_after = "build {}".format(
                mapinfo["needs_widelands_version_after"] + 1
            )

        # mapinfo["minimap"] is the absolute path to the image file
        # We move the file to the correct destination
        minimap_name = mapinfo["minimap"].rpartition("/")[2]
        minimap_upload_to = self.instance._meta.get_field("minimap").upload_to
        minimap_path = os.path.join(minimap_upload_to, minimap_name)
        self.instance.minimap = minimap_path
        shutil.move(mapinfo["minimap"], os.path.join(settings.MEDIA_ROOT, minimap_path))

        # Final cleanup
        os.remove(copied_file + ".json")
        os.remove(copied_file)

        return cleaned_data

    def save(self, *args, **kwargs):
        map = super(UploadMapForm, self).save(*args, **kwargs)
        if kwargs["commit"]:
            map.save()
        return map


class EditCommentForm(ModelForm):
    class Meta:
        model = Map
        fields = [
            "uploader_comment",
        ]
