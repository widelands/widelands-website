#!/usr/bin/env python -tt
# encoding: utf-8

import json
import subprocess

from django.forms import ModelForm
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage

from wlmaps.models import Map
import os
import shutil
import tempfile

# Seconds 'wl_map_info' may take before the upload is rejected
MAP_INFO_TIMEOUT = 60


class UploadMapForm(ModelForm):
    """
    All file operations are done in a temporary directory per upload.

    We have to handle here three different kind of files:
    1. The map which is uploaded, stored as e.g '/tmp/tmp_xyz.upload'.
       Because 'wl_map_info' can't handle files with this extension and
       produces a minimap with the same name like the initial name, the
       uploade file will be copied to a file with the name of the
       uploaded file and extension, e.g. '<tmpdir>/original_filename.wmf'
    2. 'wl_map_info' produces two files which will be stored at the same
        location as the uploaded file and named like the map file:
        a. '<tmpdir>/original_filename.wmf.json': Contains infos of the map
        b. '<tmpdir>/original_filename.wmf.png': The image of the minimap (png).

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

        safe_name = default_storage.get_valid_name(file_obj.name)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy the uploaded file to a safe filename
            copied_file = shutil.copyfile(
                file_obj.temporary_file_path(), os.path.join(tmpdir, safe_name)
            )
            self._read_map_info(copied_file)

        return cleaned_data

    def _read_map_info(self, copied_file):
        try:
            # call map info tool to generate minimap and json info file
            # run it in the Widelands directory so that the datadir is found
            wl_map_info = getattr(settings, "WIDELANDS_MAP_INFO_TOOL", "wl_map_info")
            subprocess.run(
                [wl_map_info, copied_file],
                cwd=settings.WIDELANDS_SVN_DIR,
                timeout=MAP_INFO_TIMEOUT,
                check=True,
            )
        except subprocess.CalledProcessError, subprocess.TimeoutExpired:
            self.add_error("file", "The map file could not be processed.")
            return

        with open(copied_file + ".json") as f:
            mapinfo = json.load(f)

        if Map.objects.filter(name=mapinfo["name"]).exists():
            self.add_error("file", "A map with the same name already exists.")
            return

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
            self.instance.wl_version_after = (
                f"build {mapinfo['needs_widelands_version_after'] + 1}"
            )

        # mapinfo["minimap"] is the absolute path to the image file. Store it
        # through the field, which picks a free name instead of overwriting
        # the minimap of another map uploaded under the same file name.
        with open(mapinfo["minimap"], "rb") as f:
            self.instance.minimap.save(
                os.path.basename(mapinfo["minimap"]), File(f), save=False
            )

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
