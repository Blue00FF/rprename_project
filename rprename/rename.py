# -*- coding: utf-8 -*-
# rprename/rename.py

"""This module provides the Renamer class to rename multiple files."""

from pathlib import Path
import datetime
import random
import string

from PyQt5.QtCore import QObject, pyqtSignal


class Renamer(QObject):
    """Define custom signals using pyqtSignal"""

    progress = pyqtSignal(int)
    renamed_file = pyqtSignal(Path)
    finished = pyqtSignal()

    def __init__(self, files, prefix, mode):
        super().__init__()
        self._files = files
        self._prefix = prefix
        self._mode = mode

    def rename_files(self):
        for file_number, file in enumerate(self._files, 1):
            if self._mode == "Normal Mode":
                new_file = file.parent.joinpath(
                    f"{self._prefix}{str(file_number).zfill(3)}{file.suffix}"
                )
            elif self._mode == "Datetime Mode":
                new_file = file.parent.joinpath(
                    f"{self._prefix}"
                    f"""{str(datetime.datetime.today()).replace(" ", "_")}"""
                    f"{file.suffix}"
                )
            else:
                new_file = file.parent.joinpath(
                    f"""{"".join(random.choices(string.ascii_uppercase +
                    string.digits, k=12))}{file.suffix}"""
                )
            file.rename(new_file)
            self.progress.emit(file_number)
            self.renamed_file.emit(new_file)
        self.progress.emit(0)
        self.finished.emit()
