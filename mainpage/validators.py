from django.core.exceptions import ValidationError
from django.conf import settings

import shutil
import subprocess


def virus_scan(uploaded_file):
    '''Scan uploaded_file for viruses with clamav.'''

    if settings.VIRUS_CHECK:
        tmp_file_path = uploaded_file.temporary_file_path()
        process_compl = subprocess.run(['clamdscan',
                                        '--multiscan',
                                        '--fdpass',
                                        tmp_file_path])
        if process_compl.returncode == 1:
            raise ValidationError(
                'This file seems to contain malicious code.'
                )
        if process_compl.returncode == 2:
            raise ValidationError(
                'Some error occured during virus scannning...'
            )
