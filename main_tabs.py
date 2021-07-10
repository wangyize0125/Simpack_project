# -*-coding:utf-8 -*-
# @Time    : 2021/7/4 1:57 下午
# @Author  : Yize Wang
# @File    : main_tabs.py
# @Software: PyCharm

import os
import types
import subprocess
from PyQt5.QtWidgets import QWidget, QTabWidget, QPushButton, QAbstractItemView, QLabel, QProgressBar
from PyQt5.QtWidgets import QFileDialog, QTableWidget, QTableWidgetItem, QLineEdit, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui

import public_widgets
import docx_operation
from plot_result import PlotSpk, PlotBladed, PlotSpkBladed
import public_functions as pf


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

        self.bladed_res_only = BladedResultTab(self)
        self.addTab(self.bladed_res_only, self.bladed_res_only.name)
        self.bladed_res_only.finish.connect(self.finish_slot)
        self.bladed_res_only.start.connect(self.start_slot)

        self.spck_bladed = SpkBladedResultTab(self)
        self.addTab(self.spck_bladed, self.spck_bladed.name)
        self.spck_bladed.finish.connect(self.finish_slot)
        self.spck_bladed.start.connect(self.start_slot)

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

    filter_file_format = "Result Files (*.sbr);;All Files (*)"
    filter_macro_format = "Macro (*.qs)"
    selected, unselected = ">>", "  "
    success, fail = "Suc.", "Fai."
    d_fig_size_x, d_fig_size_y = 8, 4
    d_word_filename = "Simpack result"
    d_var_file = "./resources/alias_name_spk.txt"
    d_macro_file = "./resources/macro.qs"
    simpack_post_path = "SIMPACK_POST_PATH"
    d_main_macro_file = "./resources/main.qs"
    bar_max = 1E8

    def __init__(self, parent=None):
        # initialize father widget first
        super(SpkResultTab, self).__init__(parent)

        self.setFixedSize(parent.width(), parent.height())
        self.move((parent.width() - self.width()) // 2, (parent.height() - self.height()) // 2)

        # variables must be set
        # output folder
        self.output_folder = None
        # loaded files but not selected files
        self.file_names = set()

        # upgrade progress bar
        self.step_size = 10

        # widgets
        self.l_fig_size_x, self.l_fig_size_y = QLineEdit(self), QLineEdit(self)
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
        self.choose_var_file_btn = QPushButton(self)                                # choose variable file button
        self.l_var_file = QLineEdit(self)                                           # variable file display
        self.l_macro = QLineEdit(self)                                              # macro file name
        self.choose_macro_btn = QPushButton(self)                                   # choose macro button

        # ui design for this tab
        self.ui_settings()

        return

    def ui_settings(self):
        # choose variable file button
        self.choose_var_file_btn.setText("Choose variable file")
        self.choose_var_file_btn.setFixedSize(self.width() * 0.25, self.choose_var_file_btn.height())
        self.choose_var_file_btn.move(self.width() * 0.05, self.height() * 0.03)
        self.choose_var_file_btn.clicked.connect(self.choose_var_file)

        # variable file display
        self.l_var_file.setFixedSize(self.width() * 0.6, self.l_var_file.height())
        self.l_var_file.move(self.width() * 0.35, self.height() * 0.03)
        self.l_var_file.setPlaceholderText("Keep this empty to use the default variable file")
        self.l_var_file.setFocusPolicy(Qt.NoFocus)

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

        btn_pos = 0.64
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

        # progress bar
        btn_pos += 0.05
        self.bar.setFixedSize(self.width() * 0.25, self.bar.height())
        self.bar.move(self.width() * 0.05, self.height() * btn_pos)
        self.bar.setRange(0, self.bar_max)
        self.bar.setVisible(False)

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
        self.l_docx.setPlaceholderText("Default name: {}".format(self.d_word_filename))
        self.l_docx.setVisible(self.docx_flag.checkState())

        # choose macro file button
        self.choose_macro_btn.setText("Choose macro")
        self.choose_macro_btn.setFixedSize(self.width() * 0.25, self.choose_macro_btn.height())
        self.choose_macro_btn.move(self.width() * 0.05, self.height() * 0.47)
        self.choose_macro_btn.clicked.connect(self.choose_macro)

        # macro file display
        self.l_macro.setFixedSize(self.width() * 0.25, self.l_macro.height())
        self.l_macro.move(self.width() * 0.05, self.height() * 0.53)
        self.l_macro.setPlaceholderText("Use default macro")
        self.l_macro.setFocusPolicy(Qt.NoFocus)

        return

    def choose_files(self):
        files, ok = QFileDialog.getOpenFileNames(self, "Choose files", os.getcwd(), self.filter_file_format)

        if not ok:
            pass
        else:
            # append the results into the file_names set to remove the same ones
            self.file_names.update(files)

            self.can_release_cal_btn()

            # show the files
            self.upgrade_files()

        return

    def choose_var_file(self):
        # open files
        var_file, ok = QFileDialog.getOpenFileName(self, "Choose file", os.getcwd(), "Variable file (*.txt)")

        if not ok:
            pass
        else:
            self.l_var_file.setText(var_file)

        return

    def choose_macro(self):
        # open files
        macro_file, ok = QFileDialog.getOpenFileName(self, "Choose file", os.getcwd(), self.filter_macro_format)

        if not ok:
            pass
        else:
            self.l_macro.setText(macro_file)

        return

    def upgrade_files(self):
        # set new rows
        rows = len(self.file_names)
        self.file_table.setRowCount(rows)

        # display filename
        idx = 0
        for file_name in self.file_names:
            # add the flag into the table
            flag = QTableWidgetItem(self.selected)
            flag.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.file_table.setItem(idx, 0, flag)

            # add the filename into the table
            temp_file = QTableWidgetItem(file_name)
            temp_file.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.file_table.setItem(idx, 1, temp_file)

            idx += 1

        return

    def can_release_cal_btn(self):
        # check whether the calculation button is available
        if self.file_names and self.output_folder:
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

        self.can_release_cal_btn()

        # upgrade the shown table
        self.upgrade_files()

        return

    def plot_result(self):
        # if no simpack post path, exit directly
        if self.simpack_post_path not in os.environ.keys():
            msg = public_widgets.MsgBox(self, "Lack of {} environment path".format(self.simpack_post_path))
            # no simpack post path, the following calculation cannot be done
            return

        # plot the result one-by-one
        rows = self.file_table.rowCount()

        # check how many cases are selected
        total_num, selected_files = 0, []
        for i in range(rows):
            if self.file_table.item(i, 0).text() == self.selected:
                total_num += 1
                selected_files.append(self.file_table.item(i, 1).text())

        # success flag for all the selected files
        success_flag = [True for i in range(rows)]

        if total_num == 0:
            # nothing to do
            msg_box = public_widgets.MsgBox(self, "No file selected!")
        else:
            # start calculation
            self.start.emit()

            # disable all the buttons on this tab
            self.setEnabled(False)

            # enable progress bar
            self.bar.setVisible(True)
            # set zero of the progress bar
            self.bar.setValue(0)

            self.step_size = self.bar_max / total_num / 2

            # pre process for post process
            macro_filename = self.d_macro_file if self.l_macro.text() == "" else self.l_macro.text()
            # generate the macro file with main function
            macro_file = open(os.path.join(self.output_folder, "{}_with_main.qs".format(pf.remove_suffix_of_file(macro_filename))), "w")
            main_file = open(self.d_main_macro_file, "r")
            for line in main_file.readlines():
                if "{{ macro_name }}" in line:
                    line = line.replace("{{ macro_name }}", pf.remove_suffix_of_file(macro_filename))
                macro_file.write(line)
            main_file.close()
            macro_file_without_main = open(macro_filename, "r")
            for line in macro_file_without_main.readlines():
                macro_file.write(line)
            macro_file_without_main.close()
            macro_file.close()
            # change macro_filename to the new one
            macro_filename = os.path.join(self.output_folder, "{}_with_main.qs".format(pf.remove_suffix_of_file(macro_filename)))

            # run macro for each file
            posted_files = []
            for idx, temp_filename in enumerate(selected_files):
                try:
                    sub_ps = subprocess.Popen([
                        "{}".format(os.environ[self.simpack_post_path]),         # simpack post path
                        "-s",
                        "{}".format(macro_filename),                             # macro file
                        "{}?{}".format(
                            temp_filename,                                                          # simpack res file
                            os.path.join(self.output_folder, pf.remove_suffix_of_file(temp_filename) + "_{}.txt".format(idx))
                        )
                    ])
                    ok = sub_ps.wait()
                except Exception as exc:
                    # task failed
                    ok = 1

                # update bar
                self.upgrade_bar(1)

                if os.path.isfile("debug_wangyize_1998"):
                    ok = 0

                if ok != 0:
                    err_box = public_widgets.ErrBox(self, "Spk Post {} Error".format(temp_filename))
                    posted_files.append("")

                    # record flag
                    success_flag[idx] = False
                else:
                    # change the filename in selected file list
                    posted_files.append(os.path.join(
                        self.output_folder,
                        (pf.remove_suffix_of_file(temp_filename) + "_{}.txt".format(idx))))

            # prepare input data for the calculation function
            var_file = self.d_var_file if self.l_var_file.text() == "" else self.l_var_file.text()
            # calculate size of the figures
            x, y = self.l_fig_size_x.text(), self.l_fig_size_y.text()
            x = self.d_fig_size_x if x == "" else float(x)
            y = self.d_fig_size_y if y == "" else float(y)
            # check whether output word result
            if self.docx_flag.checkState():
                word_file_name = self.d_word_filename if self.l_docx.text() == "" else self.l_docx.text()
                docx_file = docx_operation.DocxFile(os.path.join(self.output_folder, word_file_name))
            else:
                docx_file = None

            for idx, filename in enumerate(posted_files):
                try:
                    if filename:
                        pthread = PlotSpk(var_file, filename, self.output_folder, [x, y], docx_file)
                        pthread.one_file_finished.connect(self.upgrade_bar)
                        pthread.run()
                except Exception as exc:
                    err_box = public_widgets.ErrBox(self, str(exc))

                    # record flag
                    success_flag[idx] = False

            # show the flags
            self.show_success_flag(success_flag)

            # trigger finish signal for parent widget
            self.finish.emit(self.name)

            # disable progress bar
            self.bar.setVisible(False)

            # enable all buttons on this tab
            self.setEnabled(True)

        return

    def show_success_flag(self, flags: list):
        rows = self.file_table.rowCount()

        for i in range(rows):
            if self.file_table.item(i, 0).text() == self.selected:
                success_flag = QTableWidgetItem(self.success if flags[i] else self.fail)
                success_flag.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.file_table.setItem(i, 0, success_flag)

        return

    def upgrade_bar(self, num_figure):
        self.bar.setValue(self.bar.value() + self.step_size / num_figure)

        # process gui explicitly, otherwise the gui will break out
        QtGui.QGuiApplication.processEvents()

        return

    def choose_output_fld(self):
        # open folder
        self.output_folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder", os.getcwd())

        self.l_output_folder.setText(self.output_folder)

        self.can_release_cal_btn()

        return

    def docx_flap_changed(self):
        # change the line edit's state
        self.l_docx.setVisible(self.docx_flag.checkState())

        return


class BladedResultTab(QWidget):
    """
        plot Bladed result only
    """

    name = "Bladed post-process"

    finish = pyqtSignal(str)
    start = pyqtSignal()

    filter_file_format = "Bladed Project (*.$PJ);;All Files (*)"
    selected, unselected = ">>", "  "
    success, fail = "Suc.", "Fai."
    d_fig_size_x, d_fig_size_y = 8, 4
    d_word_filename = "GH-Bladed result"
    d_var_file = "./resources/alias_name_bladed.txt"
    bar_max = 1E8

    def __init__(self, parent=None):
        # initialize father widget first
        super(BladedResultTab, self).__init__(parent)

        # set fixed size and move to the center
        self.setFixedSize(parent.width(), parent.height())
        self.move((parent.width() - self.width()) // 2, (parent.height() - self.height()) // 2)

        # output folder where to output the results
        self.output_folder = None
        # loaded files but not selected files
        self.file_names = set()

        # upgrade progress bar default step size
        self.step_size = 10

        # widgets
        self.l_fig_size_x, self.l_fig_size_y = QLineEdit(self), QLineEdit(self)     # figure size input
        self.l_output_folder = QLineEdit(self)                                      # output folder display
        self.l_docx_file = QLineEdit(self)                                          # word filename input
        self.l_var_file = QLineEdit(self)                                           # variable file display
        self.choose_file_btn = QPushButton(self)                                    # choose result files
        self.unselect_all_btn = QPushButton(self)                                   # unselect all the files
        self.select_all_btn = QPushButton(self)                                     # select all the files
        self.delete_btn = QPushButton(self)                                         # delete the selected files
        self.calc_btn = QPushButton(self)                                           # start calculation button
        self.choose_out_fld_btn = QPushButton(self)                                 # choose output folder button
        self.choose_var_file_btn = QPushButton(self)                                # choose variable file button
        self.file_table = QTableWidget(self)                                        # table shows the filenames
        self.bar = QProgressBar(self)                                               # progress bar
        self.docx_flag = QCheckBox(self)                                            # whether output word file

        # ui design for this tab
        self.ui_settings()

        return

    def ui_settings(self):
        # choose variable file button
        self.choose_var_file_btn.setText("Choose variable file")
        self.choose_var_file_btn.setFixedSize(self.width() * 0.25, self.choose_var_file_btn.height())
        self.choose_var_file_btn.move(self.width() * 0.05, self.height() * 0.03)
        self.choose_var_file_btn.clicked.connect(self.choose_var_file)

        # variable file display
        self.l_var_file.setFixedSize(self.width() * 0.6, self.l_var_file.height())
        self.l_var_file.move(self.width() * 0.35, self.height() * 0.03)
        self.l_var_file.setPlaceholderText("Keep this empty to use the default variable file")
        self.l_var_file.setFocusPolicy(Qt.NoFocus)

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

        btn_pos = 0.6
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
        self.bar.move(self.width() * 0.05, self.height() * 0.8)
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
        self.l_docx_file.setFixedSize(self.width() * 0.20, self.l_fig_size_x.height())
        self.l_docx_file.move(self.width() * 0.09, self.height() * 0.41)
        self.l_docx_file.setPlaceholderText("Default name: {}".format(self.d_word_filename))
        self.l_docx_file.setVisible(self.docx_flag.checkState())

        return

    def choose_var_file(self):
        # open files
        var_file, ok = QFileDialog.getOpenFileName(self, "Choose file", os.getcwd(), "Variable file (*.txt)")

        if not ok:
            pass
        else:
            self.l_var_file.setText(var_file)

        return

    def can_release_cal_btn(self):
        if self.output_folder and self.file_names:
            self.calc_btn.setEnabled(True)
        else:
            self.calc_btn.setEnabled(False)

        return

    def choose_files(self):
        # open files
        files, ok = QFileDialog.getOpenFileNames(self, "Choose files", os.getcwd(), self.filter_file_format)

        if not ok:
            pass
        else:
            # append the results into the file_names set to remove the same ones
            self.file_names.update(files)

            self.can_release_cal_btn()

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
            flag = QTableWidgetItem(self.selected)
            flag.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.file_table.setItem(idx, 0, flag)

            # add the filename into the table
            temp_file = QTableWidgetItem(file_name)
            temp_file.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.file_table.setItem(idx, 1, temp_file)

            idx += 1

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

        self.can_release_cal_btn()

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

        # success flag for all the selected files
        success_flag = {selected_file_name: True for selected_file_name in selected_files}

        if total_num == 0:
            # nothing to do
            msg_box = public_widgets.MsgBox(self, "No file selected!")
        else:
            # start calculation trigger the start signal
            self.start.emit()

            # disable all the buttons on this tab
            self.setEnabled(False)

            # enable progress bar
            self.bar.setVisible(True)
            # set zero of the progress bar
            self.bar.setValue(0)

            self.step_size = self.bar_max / total_num / 2

            # var_file
            var_file = self.d_var_file if self.l_var_file.text() == "" else self.l_var_file.text()

            # figure size
            x, y = self.l_fig_size_x.text(), self.l_fig_size_y.text()
            x = self.d_fig_size_x if x == "" else float(x)
            y = self.d_fig_size_y if y == "" else float(y)

            # docx_file
            if self.docx_flag.checkState():
                word_file_name = self.d_word_filename if self.l_docx_file.text() == "" else self.l_docx_file.text()
                docx_file = docx_operation.DocxFile(os.path.join(self.output_folder, word_file_name))
            else:
                docx_file = None

            for filename in selected_files:
                try:
                    pthread = PlotBladed(var_file, filename, self.output_folder, [x, y], docx_file)
                    pthread.one_file_finished.connect(self.upgrade_bar)
                    pthread.run()
                except Exception as exc:
                    err_box = public_widgets.ErrBox(self, str(exc))

                    # record the flag
                    success_flag[filename] = False

            # show the flags
            self.show_success_flag(success_flag)

            # disable progress bar
            self.bar.setVisible(False)

            # enable all buttons on this tab
            self.setEnabled(True)

            # trigger finish signal for parent widget
            self.finish.emit(self.name)

        return

    def show_success_flag(self, flags: dict):
        rows = self.file_table.rowCount()

        for i in range(rows):
            if self.file_table.item(i, 1).text() in flags.keys():
                success_flag = QTableWidgetItem(self.success if flags[self.file_table.item(i, 1).text()] else self.fail)
                success_flag.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.file_table.setItem(i, 0, success_flag)

        return

    def upgrade_bar(self, num_figure):
        self.bar.setValue(self.bar.value() + self.step_size / num_figure)

        # process gui explicitly, otherwise the gui will break out
        QtGui.QGuiApplication.processEvents()

        return

    def choose_output_fld(self):
        # open folder
        self.output_folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder", os.getcwd())

        self.l_output_folder.setText(self.output_folder)

        self.can_release_cal_btn()

        return

    def docx_flap_changed(self):
        # change the line edit's state
        self.l_docx_file.setVisible(self.docx_flag.checkState())

        return


def my_drop_event(self: QTableWidget, event: QtGui.QDropEvent) -> None:
    # the items can only be moved in this table
    # original one
    original_row, original_col = self.selectedItems()[0].row(), self.selectedItems()[0].column()
    original_text = self.item(original_row, original_col).text()

    # drop where
    target_row, target_col = self.indexAt(event.pos()).row(), self.indexAt(event.pos()).column()
    if target_row == -1 or target_col == -1:
        # drag to blank area
        return
    target_text = self.item(target_row, target_col).text()

    # change the values
    if original_col == target_col and original_col != 0:
        self.item(target_row, target_col).setText(original_text)
        if original_text != "":
            self.item(target_row, target_col).setToolTip(original_text)

        self.item(original_row, original_col).setText(target_text)
        if target_text != "":
            self.item(original_row, original_col).setToolTip(target_text)

    return


class SpkBladedResultTab(QWidget):
    """
    plot and compare Simpack and Bladed results
    """

    name = "Simpack v.s. Bladed"

    finish = pyqtSignal(str)
    start = pyqtSignal()

    spck_format_filter = "Result Files (*.sbr);;All Files (*)"
    bladed_format_filter = "Bladed Project (*.$PJ);;All Files (*)"
    filter_macro_format = "Macro (*.qs)"

    selected, unselected = ">>", "  "
    success, fail = "Suc.", "Fai."

    d_fig_size_x, d_fig_size_y = 8, 4
    d_word_filename = "Simpack and GH-Bladed results"

    d_var_file_spk = "./resources/alias_name_spk.txt"
    d_var_file_bladed = "./resources/alias_name_bladed.txt"
    d_macro_file = "./resources/macro.qs"
    simpack_post_path = "SIMPACK_POST_PATH"
    d_main_macro_file = "./resources/main.qs"
    d_scale_file = "./resources/scale_factors_spk.txt"

    bar_max = 1E8
    
    def __init__(self, parent=None):
        super(SpkBladedResultTab, self).__init__(parent)

        # total init
        self.setFixedSize(parent.width(), parent.height())
        self.move((parent.width() - self.width()) // 2, (parent.height() - self.height()) // 2)

        # variables must be set
        self.output_folder = None               # output folder
        self.file_names_spk = set()             # loaded files but not selected files (spck)
        self.file_names_bladed = set()          # loaded files but not selected files (bladed)

        # upgrade progress bar
        self.step_size = 10

        # widgets for spck
        self.choose_spck_file_btn = QPushButton(self)
        self.choose_spck_var_file_btn = QPushButton(self)   # choose variable file button
        self.l_spck_var_file = QLineEdit(self)              # variable file display
        self.l_macro = QLineEdit(self)                      # macro file name
        self.choose_macro_btn = QPushButton(self)           # choose macro button
        self.choose_scale_file_btn = QPushButton(self)
        self.l_scale_file = QLineEdit(self)

        # widgets for bladed
        self.l_bladed_var_file = QLineEdit(self)  # variable file display
        self.choose_bladed_file_btn = QPushButton(self)  # choose result files
        self.choose_bladed_var_file_btn = QPushButton(self)  # choose variable file button

        # public widgets
        self.l_fig_size_x, self.l_fig_size_y = QLineEdit(self), QLineEdit(self)
        self.unselect_all_btn = QPushButton(self)
        self.select_all_btn = QPushButton(self)
        self.delete_all_btn = QPushButton(self)
        self.delete_spck_btn = QPushButton(self)
        self.delete_bladed_btn = QPushButton(self)
        self.file_table = QTableWidget(self)
        self.l_output_folder = QLineEdit(self)
        self.calc_btn = QPushButton(self)
        self.bar = QProgressBar(self)
        self.choose_out_fld_btn = QPushButton(self)
        self.l_docx = QLineEdit(self)

        # ui design for this tab
        self.ui_settings()

        return

    def ui_settings(self):
        # widgets for spck
        self.choose_spck_file_btn.setText("Choose Simpack files")
        self.choose_spck_file_btn.setFixedSize(self.width() * 0.44, self.choose_spck_file_btn.height())
        self.choose_spck_file_btn.move(self.width() * 0.05, self.height() * 0.03)
        self.choose_spck_file_btn.clicked.connect(self.choose_spck_files)

        self.choose_spck_var_file_btn.setText("Choose Simpack variable")
        self.choose_spck_var_file_btn.setFixedSize(self.width() * 0.21, self.choose_spck_var_file_btn.height())
        self.choose_spck_var_file_btn.move(self.width() * 0.05, self.height() * 0.09)
        self.choose_spck_var_file_btn.clicked.connect(self.choose_spck_var_file)

        self.l_spck_var_file.setFixedSize(self.width() * 0.21, self.l_spck_var_file.height())
        self.l_spck_var_file.move(self.width() * 0.28, self.height() * 0.09)
        self.l_spck_var_file.setPlaceholderText("Use default variable file")
        self.l_spck_var_file.setFocusPolicy(Qt.NoFocus)

        self.choose_macro_btn.setText("Choose macro")
        self.choose_macro_btn.setFixedSize(self.width() * 0.21, self.choose_macro_btn.height())
        self.choose_macro_btn.move(self.width() * 0.05, self.height() * 0.15)
        self.choose_macro_btn.clicked.connect(self.choose_macro)

        self.l_macro.setFixedSize(self.width() * 0.21, self.l_macro.height())
        self.l_macro.move(self.width() * 0.28, self.height() * 0.15)
        self.l_macro.setPlaceholderText("Use default macro")
        self.l_macro.setFocusPolicy(Qt.NoFocus)

        self.choose_scale_file_btn.setText("Choose scale simpack")
        self.choose_scale_file_btn.setFixedSize(self.width() * 0.21, self.choose_scale_file_btn.height())
        self.choose_scale_file_btn.move(self.width() * 0.05, self.height() * 0.27)
        self.choose_scale_file_btn.clicked.connect(self.choose_scale)

        self.l_scale_file.setFixedSize(self.width() * 0.21, self.l_scale_file.height())
        self.l_scale_file.move(self.width() * 0.28, self.height() * 0.27)
        self.l_scale_file.setPlaceholderText("Use default scale")
        self.l_scale_file.setFocusPolicy(Qt.NoFocus)

        # widgets for bladed
        self.choose_bladed_var_file_btn.setText("Choose Bladed variable")
        self.choose_bladed_var_file_btn.setFixedSize(self.width() * 0.21, self.choose_bladed_var_file_btn.height())
        self.choose_bladed_var_file_btn.move(self.width() * 0.51, self.height() * 0.09)
        self.choose_bladed_var_file_btn.clicked.connect(self.choose_bladed_var_file)

        self.l_bladed_var_file.setFixedSize(self.width() * 0.21, self.l_bladed_var_file.height())
        self.l_bladed_var_file.move(self.width() * 0.74, self.height() * 0.09)
        self.l_bladed_var_file.setPlaceholderText("Use default variable file")
        self.l_bladed_var_file.setFocusPolicy(Qt.NoFocus)

        self.choose_bladed_file_btn.setText("Choose Bladed files")
        self.choose_bladed_file_btn.setFixedSize(self.width() * 0.44, self.choose_bladed_file_btn.height())
        self.choose_bladed_file_btn.move(self.width() * 0.51, self.height() * 0.03)
        self.choose_bladed_file_btn.clicked.connect(self.choose_bladed_files)

        # public widgets
        l_figure_size = QLabel(self)
        l_figure_size.setText("Figure size: ")
        l_figure_size.setFixedSize(self.width() * 0.14, l_figure_size.height())
        l_figure_size.move(self.width() * 0.52, self.height() * 0.15)
        l_multi = QLabel(self)
        l_multi.setText("x")
        l_multi.setFixedSize(self.width() * 0.05, l_multi.height())
        l_multi.move(self.width() * 0.782, self.height() * 0.15)

        self.l_fig_size_x.setFixedSize(self.width() * 0.15, self.l_fig_size_x.height())
        self.l_fig_size_y.setFixedSize(self.width() * 0.15, self.l_fig_size_y.height())
        self.l_fig_size_x.move(self.width() * 0.62, self.height() * 0.15)
        self.l_fig_size_y.move(self.width() * 0.80, self.height() * 0.15)
        self.l_fig_size_x.setPlaceholderText("Width (Default: {})".format(self.d_fig_size_x))
        self.l_fig_size_y.setPlaceholderText("Height (Default {})".format(self.d_fig_size_y))

        self.unselect_all_btn.setText("Unselect all")
        self.unselect_all_btn.setFixedSize(self.width() * 0.16, self.unselect_all_btn.height())
        self.unselect_all_btn.move(self.width() * 0.05, self.height() * 0.33)
        self.unselect_all_btn.clicked.connect(self.unselect_all)

        self.select_all_btn.setText("Select all")
        self.select_all_btn.setFixedSize(self.width() * 0.16, self.select_all_btn.height())
        self.select_all_btn.move(self.width() * 0.235, self.height() * 0.33)
        self.select_all_btn.clicked.connect(self.select_all)

        self.delete_all_btn.setText("Delete selected")
        self.delete_all_btn.setFixedSize(self.width() * 0.16, self.delete_all_btn.height())
        self.delete_all_btn.move(self.width() * 0.42, self.height() * 0.33)
        self.delete_all_btn.clicked.connect(self.delete_all)

        self.delete_spck_btn.setText("Delete Simpack")
        self.delete_spck_btn.setFixedSize(self.width() * 0.16, self.delete_spck_btn.height())
        self.delete_spck_btn.move(self.width() * 0.605, self.height() * 0.33)
        self.delete_spck_btn.clicked.connect(self.delete_spck)

        self.delete_bladed_btn.setText("Delete Bladed")
        self.delete_bladed_btn.setFixedSize(self.width() * 0.16, self.delete_bladed_btn.height())
        self.delete_bladed_btn.move(self.width() * 0.79, self.height() * 0.33)
        self.delete_bladed_btn.clicked.connect(self.delete_bladed)

        self.choose_out_fld_btn.setText("Choose output folder")
        self.choose_out_fld_btn.setFixedSize(self.width() * 0.21, self.choose_out_fld_btn.height())
        self.choose_out_fld_btn.move(self.width() * 0.05, self.height() * 0.21)
        self.choose_out_fld_btn.clicked.connect(self.choose_output_fld)

        self.l_output_folder.setFixedSize(self.width() * 0.21, self.l_output_folder.height())
        self.l_output_folder.move(self.width() * 0.28, self.height() * 0.21)
        self.l_output_folder.setFocusPolicy(Qt.NoFocus)

        l_word_file = QLabel(self)
        l_word_file.setText("Word file name: ")
        l_word_file.setFixedSize(self.width() * 0.12, l_word_file.height())
        l_word_file.move(self.width() * 0.52, self.height() * 0.21)

        self.l_docx.setFixedSize(self.width() * 0.3, self.l_docx.height())
        self.l_docx.move(self.width() * 0.65, self.height() * 0.21)
        self.l_docx.setPlaceholderText("Default: {}.docx".format(self.d_word_filename))

        self.calc_btn.setText("Plot result figures")
        self.calc_btn.setFixedSize(self.width() * 0.21, self.calc_btn.height())
        self.calc_btn.move(self.width() * 0.51, self.height() * 0.27)
        self.calc_btn.clicked.connect(self.plot_result)
        self.calc_btn.setEnabled(False)

        self.bar.setFixedSize(self.width() * 0.21, self.bar.height())
        self.bar.move(self.width() * 0.74, self.height() * 0.27)
        self.bar.setRange(0, self.bar_max)
        self.bar.setVisible(False)

        self.file_table.setFixedSize(self.width() * 0.9, self.height() * 0.55)
        self.file_table.move(self.width() * 0.05, self.height() * 0.39)
        self.file_table.setColumnCount(3)
        self.file_table.setColumnWidth(0, self.file_table.width() * 0.06)
        self.file_table.setColumnWidth(1, self.file_table.width() * 0.47)
        self.file_table.setColumnWidth(2, self.file_table.width() * 0.47)
        self.file_table.setHorizontalHeaderLabels(["", "Simpack Files", "Bladed Files"])
        self.file_table.cellClicked.connect(self.cell_clicked)
        self.file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.file_table.setDragEnabled(True)
        self.file_table.setAcceptDrops(True)
        self.file_table.viewport().setAcceptDrops(True)
        self.file_table.setDragDropOverwriteMode(False)
        self.file_table.setDropIndicatorShown(True)
        self.file_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.file_table.setDragDropMode(QAbstractItemView.InternalMove)
        self.file_table.dropEvent = types.MethodType(my_drop_event, self.file_table)

        return

    def choose_spck_files(self):
        files, ok = QFileDialog.getOpenFileNames(self, "Choose Simpack files", os.getcwd(), self.spck_format_filter)

        if not ok:
            pass
        else:
            # append the results into the file_names set to remove the same ones
            self.file_names_spk.update(files)

            self.can_release_cal_btn()

            # show the files
            self.upgrade_files()

        return

    def choose_scale(self):
        # open files
        scale_file, ok = QFileDialog.getOpenFileName(self, "Choose scale file", os.getcwd(), "Scales (*.txt)")

        if not ok:
            pass
        else:
            self.l_scale_file.setText(scale_file)

        return

    def can_release_cal_btn(self):
        # check whether the calculation button is available
        if self.file_names_spk and self.file_names_bladed and self.output_folder:
            self.calc_btn.setEnabled(True)
        else:
            self.calc_btn.setEnabled(False)

        return

    def upgrade_files(self):
        # set new rows
        rows = max(len(self.file_names_spk), len(self.file_names_bladed))
        self.file_table.setRowCount(rows)

        # order the files
        ordered_spk = list(self.file_names_spk)
        ordered_bladed = list(self.file_names_bladed)
        ordered_spk.sort(), ordered_bladed.sort()

        for i in range(rows):
            # add the flag into the table
            flag = QTableWidgetItem(self.selected)
            flag.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.file_table.setItem(i, 0, flag)

            if i < len(ordered_spk):
                # add the filename into the table
                temp_file_spk = QTableWidgetItem(ordered_spk[i])
                temp_file_spk.setToolTip(ordered_spk[i])
                temp_file_spk.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.file_table.setItem(i, 1, temp_file_spk)
            else:
                # add the filename into the table
                temp_file_spk = QTableWidgetItem("")
                temp_file_spk.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.file_table.setItem(i, 1, temp_file_spk)

            if i < len(ordered_bladed):
                # add the filename into the table
                temp_file_bladed = QTableWidgetItem(ordered_bladed[i])
                temp_file_bladed.setToolTip(ordered_bladed[i])
                temp_file_bladed.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.file_table.setItem(i, 2, temp_file_bladed)
            else:
                # add the filename into the table
                temp_file_bladed = QTableWidgetItem("")
                temp_file_bladed.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.file_table.setItem(i, 2, temp_file_bladed)

        return

    def choose_bladed_files(self):
        # open files
        files, ok = QFileDialog.getOpenFileNames(self, "Choose Bladed files", os.getcwd(), self.bladed_format_filter)

        if not ok:
            pass
        else:
            # append the results into the file_names set to remove the same ones
            self.file_names_bladed.update(files)

            self.can_release_cal_btn()

            # show the files
            self.upgrade_files()

        return

    def choose_spck_var_file(self):
        # open files
        var_file, ok = QFileDialog.getOpenFileName(self, "Choose Simpack variables", os.getcwd(), "Variable (*.txt)")

        if not ok:
            pass
        else:
            self.l_spck_var_file.setText(var_file)

        return

    def choose_bladed_var_file(self):
        # open files
        var_file, ok = QFileDialog.getOpenFileName(self, "Choose Bladed variables", os.getcwd(), "Variable (*.txt)")

        if not ok:
            pass
        else:
            self.l_bladed_var_file.setText(var_file)

        return

    def choose_macro(self):
        # open files
        macro_file, ok = QFileDialog.getOpenFileName(self, "Choose macro file", os.getcwd(), self.filter_macro_format)

        if not ok:
            pass
        else:
            self.l_macro.setText(macro_file)

        return

    def unselect_all(self):
        rows = self.file_table.rowCount()

        for i in range(rows):
            self.file_table.item(i, 0).setText(self.unselected)

        return

    def select_all(self):
        rows = self.file_table.rowCount()

        for i in range(rows):
            self.file_table.item(i, 0).setText(self.selected)

        return

    def delete_all(self):
        # check how many files are selected
        rows = self.file_table.rowCount()
        for i in range(rows):
            if self.file_table.item(i, 0).text() == self.selected:
                # remove both simpack and bladed
                if self.file_table.item(i, 1).text() != "":
                    self.file_names_spk.remove(self.file_table.item(i, 1).text())
                if self.file_table.item(i, 2).text() != "":
                    self.file_names_bladed.remove(self.file_table.item(i, 2).text())

        self.can_release_cal_btn()

        # upgrade the shown table
        self.upgrade_files()

        return

    def delete_spck(self):
        # check how many files are selected
        rows = self.file_table.rowCount()
        for i in range(rows):
            if self.file_table.item(i, 0).text() == self.selected:
                # remove simpack only
                if self.file_table.item(i, 1).text() != "":
                    self.file_names_spk.remove(self.file_table.item(i, 1).text())

        self.can_release_cal_btn()

        # upgrade the shown table
        self.upgrade_files()

        return

    def delete_bladed(self):
        # check how many files are selected
        rows = self.file_table.rowCount()
        for i in range(rows):
            if self.file_table.item(i, 0).text() == self.selected:
                # remove bladed only
                if self.file_table.item(i, 2).text() != "":
                    self.file_names_bladed.remove(self.file_table.item(i, 2).text())

        self.can_release_cal_btn()

        # upgrade the shown table
        self.upgrade_files()

        return

    def choose_output_fld(self):
        # open folder
        self.output_folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder", os.getcwd())

        self.l_output_folder.setText(self.output_folder)

        self.can_release_cal_btn()

        return

    def cell_clicked(self, row, col):
        if self.file_table.item(row, 0).text() == self.selected:
            self.file_table.item(row, 0).setText(self.unselected)
        else:
            self.file_table.item(row, 0).setText(self.selected)

        return

    def plot_result(self):
        # if no simpack post path, exit directly
        if self.simpack_post_path not in os.environ.keys():
            msg = public_widgets.MsgBox(self, "Lack of {} environment path".format(self.simpack_post_path))
            # no simpack post path, the following calculation cannot be done
            return

        # plot the result one-by-one
        rows = self.file_table.rowCount()
        # check how many cases are selected
        total_num, selected_spck, selected_bladed = 0, [], []
        for i in range(rows):
            if self.file_table.item(i, 0).text() == self.selected:
                total_num += 1
                if self.file_table.item(i, 1).text() != "":
                    selected_spck.append(self.file_table.item(i, 1).text())
                if self.file_table.item(i, 2).text() != "":
                    selected_bladed.append(self.file_table.item(i, 2).text())

        # success flag for all the selected files
        success_flag = [True for i in range(total_num)]

        if total_num == 0:
            # nothing to do
            msg_box = public_widgets.MsgBox(self, "No file selected!")
        else:
            if len(selected_spck) != len(selected_bladed):
                # nothing to do
                msg_box = public_widgets.MsgBox(self, "Simpack and Bladed files do not match")
            else:
                # start calculation
                self.start.emit()

                # disable all the buttons on this tab
                self.setEnabled(False)

                # enable progress bar
                self.bar.setVisible(True)
                # set zero of the progress bar
                self.bar.setValue(0)

                self.step_size = self.bar_max / total_num / 3

                # pre process for post process
                macro_filename = self.d_macro_file if self.l_macro.text() == "" else self.l_macro.text()
                # generate the macro file with main function
                macro_file = open(
                    os.path.join(
                        self.output_folder,
                        "{}_with_main.qs".format(pf.remove_suffix_of_file(macro_filename))
                    ), "w")
                main_file = open(self.d_main_macro_file, "r")
                for line in main_file.readlines():
                    if "{{ macro_name }}" in line:
                        line = line.replace("{{ macro_name }}", pf.remove_suffix_of_file(macro_filename))
                    macro_file.write(line)
                main_file.close()
                macro_file_without_main = open(macro_filename, "r")
                for line in macro_file_without_main.readlines():
                    macro_file.write(line)
                macro_file_without_main.close()
                macro_file.close()
                # change macro_filename to the new one
                macro_filename = os.path.join(
                    self.output_folder,
                    "{}_with_main.qs".format(pf.remove_suffix_of_file(macro_filename))
                )

                # run macro for each simpack file
                posted_spk_files = []
                for idx, temp_filename in enumerate(selected_spck):
                    try:
                        sub_ps = subprocess.Popen([
                            "{}".format(os.environ[self.simpack_post_path]),  # path
                            "-s",
                            "{}".format(macro_filename),  # macro file
                            "{}?{}".format(
                                temp_filename,  # simpack res file
                                os.path.join(
                                    self.output_folder,
                                    (pf.remove_suffix_of_file(temp_filename) + "_{}.txt").format(idx)
                                ))
                        ])
                        # wait until it finished
                        ok = sub_ps.wait()
                    except Exception as exc:
                        # task failed
                        ok = 1

                    # update bar
                    self.upgrade_bar(1)

                    if os.path.isfile("debug_wangyize_1998"):
                        ok = 0

                    if ok != 0:
                        err_box = public_widgets.ErrBox(self, "Spk Post {} Error".format(temp_filename))
                        posted_spk_files.append("")
                        # record flag
                        success_flag[idx] = False
                    else:
                        # change the filename in selected file list
                        posted_spk_files.append(os.path.join(
                            self.output_folder,
                            (pf.remove_suffix_of_file(temp_filename) + "_{}.txt").format(idx)
                        ))

                # prepare input data for the calculation function
                vf_spck = self.d_var_file_spk if self.l_spck_var_file.text() == "" else self.l_spck_var_file.text()
                vf_bld = self.d_var_file_bladed if not self.l_bladed_var_file.text() else self.l_bladed_var_file.text()

                # calculate size of the figures
                x, y = self.l_fig_size_x.text(), self.l_fig_size_y.text()
                x = self.d_fig_size_x if not x else float(x)
                y = self.d_fig_size_y if not y else float(y)

                # check whether output word result
                word_file_name = self.d_word_filename if self.l_docx.text() == "" else self.l_docx.text()
                docx_file = docx_operation.DocxFile(os.path.join(self.output_folder, word_file_name))

                # scale file
                scale_file = self.d_scale_file if not self.l_scale_file.text() else self.l_scale_file.text()

                # simpack one by one
                for file_spck, file_bladed in zip(posted_spk_files, selected_bladed):
                    try:
                        if file_spck:
                            pthread = PlotSpkBladed(
                                vf_spck, file_spck, vf_bld, file_bladed, scale_file,
                                self.output_folder, [x, y], docx_file
                            )
                            pthread.one_file_finished.connect(self.upgrade_bar)
                            pthread.run()
                    except Exception as exc:
                        err_box = public_widgets.ErrBox(self, str(exc))

                        # record flag
                        success_flag[posted_spk_files.index(file_spck)] = False

                # show the flags
                self.show_success_flag(success_flag)

                # trigger finish signal for parent widget
                self.finish.emit(self.name)

                # disable progress bar
                self.bar.setVisible(False)

                # enable all buttons on this tab
                self.setEnabled(True)

        return

    def upgrade_bar(self, num):
        self.bar.setValue(self.bar.value() + self.step_size / num)

        # process gui explicitly, otherwise the gui will break out
        QtGui.QGuiApplication.processEvents()

        return

    def show_success_flag(self, flags: list):
        rows = self.file_table.rowCount()

        select_idx = -1
        for i in range(rows):
            if self.file_table.item(i, 0).text() == self.selected:
                select_idx += 1

                success_flag = QTableWidgetItem(self.success if flags[select_idx] else self.fail)
                success_flag.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.file_table.setItem(i, 0, success_flag)

        return
