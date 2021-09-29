# -*- coding: utf-8 -*-
# rprename/views.py

"""This module provides the RP Renamer main window."""

from collections import deque
from pathlib import Path

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QFileDialog

from .rename import Renamer
from .ui.window import Ui_Window

FILTERS = ";;".join(
    (
        "PNG Files (*.png)",
        "JPEG Files (*.jpeg)",
        "JPG Files (*.jpg)",
        "GIF Files (*.gif)",
        "BMP Files (*.bmp)",
        "Text Files (*.txt)",
        "Document Files (*.docx)",
        "Spreadsheet Files (*.xlsx)",
        "Python Files (*.py)",
    )
)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self._files = deque()
        self._files_count = len(self._files)
        self.ui = Ui_Window()
        self._setup_ui()
        self._connect_signals_slots()

    def _setup_ui(self):
        self.ui.setupUi(self)
        self._update_state_no_files()

    def _update_state_no_files(self):
        self._files_count = len(self._files)
        self.loadFilesButton.setEnabled(True)
        self.loadFilesButton.setFocus(True)
        self.renameFilesButton.setEnabled(False)
        self.prefixEdit.clear()
        self.prefixEdit.setEnabled(False)

    def _connect_signals_slots(self):
        self.loadFilesButton.clicked.connect(self.load_files)
        self.renameFilesButton.clicked.connect(self.rename_files)
        self.prefixEdit.textChanged.connect(self._update_state_ready)

    def _update_state_ready(self):
        if self.prefixEdit.text():
            self.renameFilesButton.setEnabled(True)
        else:
            self.renameFilesButton.setEnabled(False)

    def load_files(self):
        self.dstFileList.clear()
        if self.dirEdit.text():
            init_dir = self.dirEdit.text()
        else:
            init_dir = str(Path.home())
        files, filter = QFileDialog.getOpenFileNames(
            self, "Choose Files to Rename", init_dir, filter=FILTERS
        )
        if len(files) > 0:
            file_extension = filter[filter.index("*"): -1]
            self.extensionLabel.setText(file_extension)
            src_dir_name = str(Path(files[0]).parent)
            self.dirEdit.setText(src_dir_name)
            for file in files:
                self._files.append(Path(file))
                self.srcFileList.addItem(file)
            self._files_count = len(self._files)
            self._update_state_files_loaded()

    def _update_state_files_loaded(self):
        self.prefixEdit.setEnabled(True)
        self.prefixEdit.setEnabled(True)

    def rename_files(self):
        self._run_renamer_thread()
        self._update_state_renaming()

    def _run_renamer_thread(self):
        prefix = self.prefixEdit.text()
        self._thread = QThread()
        self._renamer = Renamer(
            files=tuple(self._files),
            prefix=prefix,
        )
        self._renamer.moveToThread(self._thread)
        self._thread.started.connect(self._renamer.rename_files)
        self._renamer.renamed_file.connect(self._update_state_after_rename)
        self._renamer.progress.connect(self._update_progress_bar)
        self._renamer.finished.connect(self._update_state_no_files)
        self._renamer.finished.connect(self._thread.quit)
        self._renamer.finished.connect(self._renamer.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _update_state_renaming(self):
        self.loadFilesButton.setEnabled(False)
        self.renameFilesButton.setEnabled(False)

    def _update_state_after_rename(self, new_file):
        self._files.popleft()
        self.srcFileList.takeItem(0)
        self.dstFileList.addItem(str(new_file))

    def _update_progress_bar(self, file_number):
        progress_percent = int(file_number/self._files_count * 100)
        self.progressBar.setValue(progress_percent)
