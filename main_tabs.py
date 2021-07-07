# -*-coding:utf-8 -*-
# @Time    : 2021/7/4 1:57 下午
# @Author  : Yize Wang
# @File    : main_tabs.py
# @Software: PyCharm

import os
from PyQt5.QtWidgets import QWidget, QTabWidget, QPushButton, QAbstractItemView, QLabel, QProgressBar
from PyQt5.QtWidgets import QFileDialog, QTableWidget, QTableWidgetItem, QLineEdit, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui

import public_widgets
import docx_operation
from plot_spk_result import PlotSpk


class MainTab(QTabWidget):
    """
    Main tab widget shown in the main window
    """

    finish = pyqtSignal(str)
    start = pyqtSignal()

    size = 0.9

    def __init__(self, parent=None):
        # initialize father widget first
        super(MainTab, self).__init__(parent)

        # resize and make it center
        self.setFixedSize(parent.width() * self.size, parent.height() * self.size)
        self.move((parent.width() - self.width()) // 2, (parent.height() - self.height()) // 2)

        # create tab widgets
        self.spk_res_only = SpkResultTab(self)
        self.addTab(self.spk_res_only, self.spk_res_only.name)
        self.spk_res_only.finish.connect(self.finish_slot)
        self.spk_res_only.start.connect(self.start_slot)

        return

    def finish_slot(self, msg):
        self.finish.emit(msg)

        return

    def start_slot(self):
        self.start.emit()

        return


class SpkResultTab(QWidget):
    """
    plot simpack result only
    """

    name = "Simpack post-process"

    finish = pyqtSignal(str)
    start = pyqtSignal()

    filter_file_format = "Text Files (*.txt);;All Files (*)"
    selected, unselected = ">>", "  "
    d_fig_size_x, d_fig_size_y = 8, 4
    d_word_filename = "Simpack result"
    bar_max = 1E8

    def __init__(self, parent=None):
        # initialize father widget first
        super(SpkResultTab, self).__init__(parent)

        self.setFixedSize(parent.width(), parent.height())
        self.move((parent.width() - self.width()) // 2, (parent.height() - self.height()) // 2)

        # output folder where to output the results
        self.output_folder = None

        # figure size input
        self.l_fig_size_x, self.l_fig_size_y = QLineEdit(self), QLineEdit(self)

        # upgrade progress bar
        self.step_size = 10

        # selected files
        self.file_names = set()

        # widgets
        self.choose_file_btn = QPushButton(self)
        self.unselect_all_btn = QPushButton(self)
        self.select_all_btn = QPushButton(self)
        self.delete_btn = QPushButton(self)
        self.file_table = QTableWidget(self)
        self.l_output_folder = QLineEdit(self)
        self.calc_btn = QPushButton(self)
        self.bar = QProgressBar(self)
        self.choose_out_fld_btn = QPushButton(self)
        self.docx_flag = QCheckBox(self)
        self.l_docx = QLineEdit(self)

        # ui design for this tab
        self.spk_res_only_ui()

        return

    def spk_res_only_ui(self):
        # choose file button
        self.choose_file_btn.setText("Choose files")
        self.choose_file_btn.setFixedSize(self.width() * 0.25, self.choose_file_btn.height())
        self.choose_file_btn.move(self.width() * 0.05, self.height() * 0.1)
        self.choose_file_btn.clicked.connect(self.choose_files)

        # filename table
        self.file_table.setFixedSize(self.width() * 0.6, self.height() * 0.75)
        self.file_table.move(self.width() * 0.35, self.height() * 0.1)
        self.file_table.setColumnCount(2)
        self.file_table.setColumnWidth(0, self.file_table.width() * 0.1)
        self.file_table.setColumnWidth(1, self.file_table.width() * 0.9)
        self.file_table.setHorizontalHeaderLabels(["", "Filename"])
        self.file_table.cellClicked.connect(self.cell_clicked)
        self.file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        btn_pos = 0.5
        # cancel select all button
        self.unselect_all_btn.setText("Unselect all")
        self.unselect_all_btn.setFixedSize(self.width() * 0.25, self.unselect_all_btn.height())
        self.unselect_all_btn.move(self.width() * 0.05, self.height() * btn_pos)
        self.unselect_all_btn.clicked.connect(self.unselected_all)

        # select all button
        btn_pos += 0.05
        self.select_all_btn.setText("Select all")
        self.select_all_btn.setFixedSize(self.width() * 0.25, self.select_all_btn.height())
        self.select_all_btn.move(self.width() * 0.05, self.height() * btn_pos)
        self.select_all_btn.clicked.connect(self.select_all)

        # delete button
        btn_pos += 0.05
        self.delete_btn.setText("Delete selected files")
        self.delete_btn.setFixedSize(self.width() * 0.25, self.delete_btn.height())
        self.delete_btn.move(self.width() * 0.05, self.height() * btn_pos)
        self.delete_btn.clicked.connect(self.delete)

        # calculation button
        btn_pos += 0.05
        self.calc_btn.setText("Plot result figures")
        self.calc_btn.setFixedSize(self.width() * 0.25, self.calc_btn.height())
        self.calc_btn.move(self.width() * 0.05, self.height() * btn_pos)
        self.calc_btn.clicked.connect(self.plot_result)
        self.calc_btn.setEnabled(False)

        # choose output folder button
        self.choose_out_fld_btn.setText("Choose output folder")
        self.choose_out_fld_btn.setFixedSize(self.width() * 0.25, self.choose_out_fld_btn.height())
        self.choose_out_fld_btn.move(self.width() * 0.05, self.height() * 0.9)
        self.choose_out_fld_btn.clicked.connect(self.choose_output_fld)

        # display folder
        self.l_output_folder.setFixedSize(self.width() * 0.6, self.l_output_folder.height())
        self.l_output_folder.move(self.width() * 0.35, self.height() * 0.9)
        self.l_output_folder.setFocusPolicy(Qt.NoFocus)

        # figure size
        l_figure_size = QLabel(self)
        l_figure_size.setText("Figure size")
        l_figure_size.setFixedSize(self.width() * 0.3, l_figure_size.height())
        l_figure_size.move(self.width() * 0.06, self.height() * 0.17)
        l_size_x, l_size_y = QLabel(self), QLabel(self)
        l_size_x.setText("x: "), l_size_y.setText("y: ")
        l_size_x.setFixedSize(self.width() * 0.1, l_size_x.height())
        l_size_y.setFixedSize(self.width() * 0.1, l_size_y.height())
        l_size_x.move(self.width() * 0.06, self.height() * 0.23)
        l_size_y.move(self.width() * 0.06, self.height() * 0.29)

        self.l_fig_size_x.setFixedSize(self.width() * 0.20, self.l_fig_size_x.height())
        self.l_fig_size_y.setFixedSize(self.width() * 0.20, self.l_fig_size_y.height())
        self.l_fig_size_x.move(self.width() * 0.09, self.height() * 0.23)
        self.l_fig_size_y.move(self.width() * 0.09, self.height() * 0.29)
        self.l_fig_size_x.setPlaceholderText("Default {}".format(self.d_fig_size_x))
        self.l_fig_size_y.setPlaceholderText("Default {}".format(self.d_fig_size_y))

        # progress bar
        self.bar.setFixedSize(self.width() * 0.25, self.bar.height())
        self.bar.move(self.width() * 0.05, self.height() * 0.7)
        self.bar.setRange(0, self.bar_max)
        self.bar.setVisible(False)

        # docx output check box
        self.docx_flag.move(self.width() * 0.06, self.height() * 0.37)
        self.docx_flag.setCheckState(False)
        self.docx_flag.stateChanged.connect(self.docx_flap_changed)
        docx_label = QLabel(self)
        docx_label.setText("Output results in word")
        docx_label.setFixedSize(self.width() * 0.3, l_figure_size.height())
        docx_label.move(self.width() * 0.09, self.height() * 0.358)

        # docx name line edit
        self.l_docx.setFixedSize(self.width() * 0.20, self.l_fig_size_x.height())
        self.l_docx.move(self.width() * 0.09, self.height() * 0.41)
        self.l_docx.setPlaceholderText("Default name: {})".format(self.d_word_filename))
        self.l_docx.setVisible(False)

        return

    def choose_files(self):
        # open files
        files, ok = QFileDialog.getOpenFileNames(self, "Choose files", os.getcwd(), self.filter_file_format)

        if not ok:
            pass
        else:
            # append the results into the file_names set to remove the same ones
            self.file_names.update(files)

            # show the files
            self.upgrade_files()

        return

    def upgrade_files(self):
        # set new rows
        rows = len(self.file_names)
        self.file_table.setRowCount(rows)

        # display filename
        idx = 0
        for file_name in self.file_names:
            # add the flag into the table
            flag = QTableWidgetItem(self.unselected)
            flag.setTextAlignment(Qt.AlignRight)
            self.file_table.setItem(idx, 0, flag)

            # add the filename into the table
            self.file_table.setItem(idx, 1, QTableWidgetItem(file_name))

            idx += 1

        # check whether the calculation button is available
        if len(self.file_names) > 0 and self.output_folder is not None:
            self.calc_btn.setEnabled(True)
        else:
            self.calc_btn.setEnabled(False)

        return

    def cell_clicked(self, row, col):
        if self.file_table.item(row, 0).text() == self.selected:
            self.file_table.item(row, 0).setText(self.unselected)
        else:
            self.file_table.item(row, 0).setText(self.selected)

        return

    def unselected_all(self):
        rows = self.file_table.rowCount()

        for i in range(rows):
            self.file_table.item(i, 0).setText(self.unselected)

        return

    def select_all(self):
        rows = self.file_table.rowCount()

        for i in range(rows):
            self.file_table.item(i, 0).setText(self.selected)

        return

    def delete(self):
        # check how many files are selected
        rows = self.file_table.rowCount()
        for i in range(rows):
            if self.file_table.item(i, 0).text() == self.selected:
                self.file_names.remove(self.file_table.item(i, 1).text())

        # upgrade the shown table
        self.upgrade_files()

        return

    def plot_result(self):
        # plot the result one-by-one
        rows = self.file_table.rowCount()

        # check how many cases are selected
        total_num = 0
        selected_files = []
        for i in range(rows):
            if self.file_table.item(i, 0).text() == self.selected:
                total_num += 1
                selected_files.append(self.file_table.item(i, 1).text())

        if total_num == 0:
            # nothing to do
            msg_box = public_widgets.MsgBox(self, "No file selected!")
        else:
            # start calculation
            self.start.emit()

            # disable all the buttons on this tab
            self.setEnabled(False)

            # calculate size of the figures
            x, y = self.l_fig_size_x.text(), self.l_fig_size_y.text()
            x = self.d_fig_size_x if x == "" else float(x)
            y = self.d_fig_size_y if y == "" else float(y)

            # check whether output word result
            if self.docx_flag.checkState():
                word_file_name = self.l_docx.text()
                if word_file_name == "":
                    docx_file = docx_operation.DocxFile(os.path.join(self.output_folder, self.d_word_filename))
                else:
                    docx_file = docx_operation.DocxFile(os.path.join(self.output_folder, word_file_name))
            else:
                docx_file = None

            # enable progress bar
            self.bar.setVisible(True)
            # set zero of the progress bar
            self.bar.setValue(0)

            self.step_size = self.bar_max / total_num

            for filename in selected_files:
                try:
                    pthread = PlotSpk(filename, self.output_folder, [x, y], docx_file)

                    pthread.one_file_finished.connect(self.upgrade_bar)
                    pthread.run()
                except Exception as exc:
                    err_box = public_widgets.ErrBox(self, str(exc))

            # trigger finish signal for parent widget
            self.finish.emit(self.name)

            # disable progress bar
            self.bar.setVisible(False)

            # enable all buttons on this tab
            self.setEnabled(True)

        return

    def upgrade_bar(self, num_figure):
        self.bar.setValue(self.bar.value() + self.step_size / num_figure)

        # process gui explicitly, otherwise the gui will break out
        QtGui.QGuiApplication.processEvents()

        return

    def choose_output_fld(self):
        # open folder
        self.output_folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder", os.getcwd())

        # display folder
        self.upgrade_folder()

        return

    def upgrade_folder(self):
        self.l_output_folder.setText(self.output_folder)

        # check whether the calculation button is available
        if len(self.file_names) > 0 and self.output_folder is not None:
            self.calc_btn.setEnabled(True)
        else:
            self.calc_btn.setEnabled(False)

        return

    def docx_flap_changed(self):
        # change the line edit's state
        self.l_docx.setVisible(not self.l_docx.isVisible())

        return
