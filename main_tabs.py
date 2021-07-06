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
import plot_spk_result


class MainTab(QTabWidget):
    """
    Main tab widget shown in the main window
    """

    finish = pyqtSignal(str)
    start = pyqtSignal()

    filter_file_format = "Text Files (*.txt);;All Files (*)"

    def __init__(self, parent=None, size=0.9):
        # initialize father widget first
        super(MainTab, self).__init__(parent)

        self.parent = parent
        self.output_folder = None

        # default figure size
        self.default_x = 8
        self.default_y = 4

        # create tab widgets
        self.spk_res_only = QWidget(self)
        self.addTab(self.spk_res_only, "Simpack Result")

        # figure size input
        self.display_x = QLineEdit(self.spk_res_only)
        self.display_y = QLineEdit(self.spk_res_only)

        self.default_word_filename = "Simpack result"

        # upgrade progress bar
        self.step_size = 10

        # resize and make it center
        self.setFixedSize(parent.width() * size, parent.height() * size)
        self.move((parent.width() - self.width()) // 2, (parent.height() - self.height()) // 2)

        # widgets
        self.choose_file_btn_spk = QPushButton(self.spk_res_only)
        self.unselect_all_btn_spk = QPushButton(self.spk_res_only)
        self.select_all_btn_spk = QPushButton(self.spk_res_only)
        self.delete_btn_spk = QPushButton(self.spk_res_only)
        self.spk_file_table = QTableWidget(self.spk_res_only)
        self.spk_display_folder = QLineEdit(self.spk_res_only)
        self.calc_btn_spk = QPushButton(self.spk_res_only)
        self.file_names_spk = set()
        self.bar_spk = QProgressBar(self.spk_res_only)
        self.bar_max = 1E8
        self.choose_out_fld_spk = QPushButton(self.spk_res_only)
        self.docx_flag_spk = QCheckBox(self.spk_res_only)
        self.docx_spk = QLineEdit(self.spk_res_only)

        # change simpack only ui design
        self.spk_res_only_ui()

        self.bld_res_only = QWidget(self)
        self.addTab(self.bld_res_only, "Blade Result")
        self.bld_res_only_ui()

        return

    def spk_res_only_ui(self):
        # choose file button
        self.choose_file_btn_spk.setText("Choose simpack results")
        self.choose_file_btn_spk.setFixedSize(self.width() * 0.25, self.choose_file_btn_spk.height())
        self.choose_file_btn_spk.move(self.width() * 0.05, self.height() * 0.1)
        self.choose_file_btn_spk.clicked.connect(self.choose_spk_files)

        # filename table
        self.spk_file_table.setFixedSize(self.width() * 0.6, self.height() * 0.75)
        self.spk_file_table.move(self.width() * 0.35, self.height() * 0.1)
        self.spk_file_table.setColumnCount(1)
        self.spk_file_table.setColumnWidth(0, self.spk_file_table.width())
        self.spk_file_table.setHorizontalHeaderLabels(["Filename"])
        self.spk_file_table.cellClicked.connect(self.cell_clicked)
        self.spk_file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        btn_pos = 0.5
        # cancel select all button
        self.unselect_all_btn_spk.setText("Unselect all")
        self.unselect_all_btn_spk.setFixedSize(self.width() * 0.25, self.unselect_all_btn_spk.height())
        self.unselect_all_btn_spk.move(self.width() * 0.05, self.height() * btn_pos)
        self.unselect_all_btn_spk.clicked.connect(self.cancel_select_all_spk)

        # select all button
        btn_pos += 0.05
        self.select_all_btn_spk.setText("Select all")
        self.select_all_btn_spk.setFixedSize(self.width() * 0.25, self.select_all_btn_spk.height())
        self.select_all_btn_spk.move(self.width() * 0.05, self.height() * btn_pos)
        self.select_all_btn_spk.clicked.connect(self.select_all_spk)

        # delete button
        btn_pos += 0.05
        self.delete_btn_spk.setText("Delete selected files")
        self.delete_btn_spk.setFixedSize(self.width() * 0.25, self.delete_btn_spk.height())
        self.delete_btn_spk.move(self.width() * 0.05, self.height() * btn_pos)
        self.delete_btn_spk.clicked.connect(self.delete_spk)

        # calculation button
        btn_pos += 0.05
        self.calc_btn_spk.setText("Plot result figures")
        self.calc_btn_spk.setFixedSize(self.width() * 0.25, self.calc_btn_spk.height())
        self.calc_btn_spk.move(self.width() * 0.05, self.height() * btn_pos)
        self.calc_btn_spk.clicked.connect(self.plot_result_spk)
        self.calc_btn_spk.setEnabled(False)

        # choose output folder button
        self.choose_out_fld_spk.setText("Choose output folder")
        self.choose_out_fld_spk.setFixedSize(self.width() * 0.25, self.choose_out_fld_spk.height())
        self.choose_out_fld_spk.move(self.width() * 0.05, self.height() * 0.9)
        self.choose_out_fld_spk.clicked.connect(self.choose_output_folder)

        # display folder
        self.spk_display_folder.setFixedSize(self.width() * 0.6, self.spk_display_folder.height())
        self.spk_display_folder.move(self.width() * 0.35, self.height() * 0.9)
        self.spk_display_folder.setFocusPolicy(Qt.NoFocus)

        # figure size
        l_figure_size = QLabel(self.spk_res_only)
        l_figure_size.setText("Figure size")
        l_figure_size.setFixedSize(self.width() * 0.3, l_figure_size.height())
        l_figure_size.move(self.width() * 0.06, self.height() * 0.17)
        l_size_x, l_size_y = QLabel(self.spk_res_only), QLabel(self.spk_res_only)
        l_size_x.setText("x: "), l_size_y.setText("y: ")
        l_size_x.setFixedSize(self.width() * 0.1, l_size_x.height())
        l_size_y.setFixedSize(self.width() * 0.1, l_size_y.height())
        l_size_x.move(self.width() * 0.06, self.height() * 0.23)
        l_size_y.move(self.width() * 0.06, self.height() * 0.29)

        self.display_x.setFixedSize(self.width() * 0.20, self.display_x.height())
        self.display_y.setFixedSize(self.width() * 0.20, self.display_y.height())
        self.display_x.move(self.width() * 0.09, self.height() * 0.23)
        self.display_y.move(self.width() * 0.09, self.height() * 0.29)
        self.display_x.setPlaceholderText("Default {}".format(self.default_x))
        self.display_y.setPlaceholderText("Default {}".format(self.default_y))

        # progress bar
        self.bar_spk.setFixedSize(self.width() * 0.25, self.bar_spk.height())
        self.bar_spk.move(self.width() * 0.05, self.height() * 0.7)
        self.bar_spk.setRange(0, self.bar_max)
        self.bar_spk.setVisible(False)

        # docx output check box
        self.docx_flag_spk.move(self.width()*0.06, self.height() * 0.37)
        self.docx_flag_spk.setCheckState(False)
        self.docx_flag_spk.stateChanged.connect(self.docx_flap_changed)
        docx_label = QLabel(self.spk_res_only)
        docx_label.setText("Output results in word")
        docx_label.setFixedSize(self.width() * 0.3, l_figure_size.height())
        docx_label.move(self.width() * 0.09, self.height() * 0.358)

        # docx name line edit
        self.docx_spk.setFixedSize(self.width() * 0.20, self.display_x.height())
        self.docx_spk.move(self.width() * 0.09, self.height() * 0.41)
        self.docx_spk.setPlaceholderText("Default name: {})".format(self.default_word_filename))
        self.docx_spk.setVisible(False)

        return

    def choose_spk_files(self):
        # open files
        files, ok = QFileDialog.getOpenFileNames(self, "Choose Simpack Results", os.getcwd(), self.filter_file_format)

        if not ok:
            pass
        else:
            self.file_names_spk.update(files)

        # show the files
        self.upgrade_spk_files()

        return

    def upgrade_spk_files(self):
        # set new rows
        rows = len(self.file_names_spk)
        self.spk_file_table.setRowCount(rows)

        # display filename
        idx = 0
        for file_name in self.file_names_spk:
            file = QTableWidgetItem(file_name)
            file.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            file.setCheckState(Qt.Unchecked)
            self.spk_file_table.setItem(idx, 0, file)

            idx += 1

        # check whether the calculation button is available
        if len(self.file_names_spk) > 0 and self.output_folder is not None:
            self.calc_btn_spk.setEnabled(True)
        else:
            self.calc_btn_spk.setEnabled(False)

        return

    def select_all_spk(self):
        rows = self.spk_file_table.rowCount()

        for i in range(rows):
            self.spk_file_table.item(i, 0).setCheckState(Qt.Checked)

        return

    def cancel_select_all_spk(self):
        rows = self.spk_file_table.rowCount()

        for i in range(rows):
            self.spk_file_table.item(i, 0).setCheckState(Qt.Unchecked)

        return

    def delete_spk(self):
        # check how many files are selected
        rows = self.spk_file_table.rowCount()
        for i in range(rows):
            if self.spk_file_table.item(i, 0).checkState():
                self.file_names_spk.remove(self.spk_file_table.item(i, 0).text())

        # upgrade the shown table
        self.upgrade_spk_files()

        return

    def choose_output_folder(self):
        # open folder
        self.output_folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder", os.getcwd())

        # display folder
        self.upgrade_folder()

        return

    def upgrade_folder(self):
        self.spk_display_folder.setText(self.output_folder)

        # check whether the calculation button is available
        if len(self.file_names_spk) > 0 and self.output_folder is not None:
            self.calc_btn_spk.setEnabled(True)
        else:
            self.calc_btn_spk.setEnabled(False)

        return

    def plot_result_spk(self):
        # plot the result one-by-one
        rows = self.spk_file_table.rowCount()
        # check how many cases are selected
        total_num = 0
        for i in range(rows):
            if self.spk_file_table.item(i, 0).checkState():
                total_num += 1

        if total_num == 0:
            # nothing to do
            msg_box = public_widgets.MsgBox(self, "No file selected!")
        else:
            # disable all the buttons on this tab
            self.spk_res_only.setEnabled(False)

            # calculate size of the figures
            x = self.display_x.text()
            y = self.display_y.text()
            if x == "":
                x = self.default_x
            else:
                x = float(x)
            if y == "":
                y = self.default_y
            else:
                y = float(y)
            size = (x, y)

            # check whether output word result
            if self.docx_flag_spk.checkState():
                word_file_name = self.docx_spk.text()
                if word_file_name == "":
                    docx_file = docx_operation.DocxFile(os.path.join(self.output_folder, self.default_word_filename))
                else:
                    docx_file = docx_operation.DocxFile(os.path.join(self.output_folder, word_file_name))
            else:
                docx_file = None

            # enable progress bar
            self.bar_spk.setVisible(True)
            # set zero of the progress bar
            self.bar_spk.setValue(0)

            self.step_size = self.bar_max / total_num

            for i in range(rows):
                if self.spk_file_table.item(i, 0).checkState():
                    # if it is checked, calculate the results
                    try:
                        pthread = plot_spk_result.PlotSpk(self.spk_file_table.item(i, 0).text(), self.output_folder, size, docx_file)

                        pthread.one_file_finished.connect(self.upgrade_bar)
                        pthread.run()
                    except Exception as exc:
                        err_box = public_widgets.ErrBox(self, str(exc))

            # trigger finish signal for parent widget
            self.finish.emit("Simpack")

            # disable progress bar
            self.bar_spk.setVisible(False)

            # enable all buttons on this tab
            self.spk_res_only.setEnabled(True)

        return

    def upgrade_bar(self, num_figure):
        self.bar_spk.setValue(self.bar_spk.value() + self.step_size / num_figure)

        # process gui explicitly, otherwise the gui will break out
        QtGui.QGuiApplication.processEvents()

        return

    def docx_flap_changed(self):
        # change the line edit's state
        self.docx_spk.setVisible(not self.docx_spk.isVisible())

        return

    def cell_clicked(self, row, col):
        self.spk_file_table.item(row, col).setCheckState(not self.spk_file_table.item(row, col).checkState())

        return

    def bld_res_only_ui(self):
        pass
