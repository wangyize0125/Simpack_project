# -*-coding:utf-8 -*-
# @Time    : 2021/7/4 5:00 下午
# @Author  : Yize Wang
# @File    : plot_result.py
# @Software: PyCharm

import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from PyQt5.QtCore import pyqtSignal, QObject

import load_result
import docx_operation
import public_functions as pf

matplotlib.rcParams['xtick.direction'] = 'in'
matplotlib.rcParams['ytick.direction'] = 'in'

# change font style
config = {
    "font.family": "Times New Roman",
    "font.size": 14,
}
matplotlib.rcParams.update(config)


class PlotSpk(QObject):
    """
    encapsulate plot simpack result
    """

    one_file_finished = pyqtSignal(int)            # finish one file trigger

    def __init__(self, var_file: str, filename: str, output_folder: str, size: list, out_docx: docx_operation.DocxFile):
        super(PlotSpk, self).__init__()

        self.var_file = var_file
        self.filename = filename
        self.output_folder = output_folder
        self.size = size
        self.docx_file = out_docx

        return

    def run(self):
        # output docx file
        if self.docx_file:
            self.docx_file.add_heading(self.filename, 1)

        spk_res = load_result.SpkResult(self.var_file, self.filename)
        res, order = spk_res.get_result(), spk_res.get_order()

        # calculate output file name prefix
        file_prefix = os.path.join(self.output_folder, pf.remove_suffix_of_file(self.filename)) + "_"

        time = None
        for alias, value in res.items():
            if alias.lower() == "time":
                time = value

        for alias in order:
            if alias.lower() != "time":
                self.__plot(time, res[alias], self.size, file_prefix + alias)

                self.one_file_finished.emit(len(order) - 1)

        return

    def __plot(self, x: np.ndarray, y: np.ndarray, size, output_name):
        fig = plt.figure(figsize=size)
        plt.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.90)

        # skip some results and unit x and y size
        total_num = min(x.size, y.size)
        x, y = x[0: total_num], y[0: total_num]

        # plot
        ax = plt.subplot(111, label="Simpack")
        ax.plot(x, y)
        ax.set_title(os.path.basename(output_name))

        # automatic limit
        x_lim = (np.min(x), np.max(x))
        if x_lim[0] == x_lim[1]:
            x_lim[0] -= 0.5
            x_lim[1] += 0.5
        x_major, x_minor = MultipleLocator((x_lim[1] - x_lim[0]) / 10), MultipleLocator((x_lim[1] - x_lim[0]) / 50)
        y_min, y_max = np.min(y), np.max(y)
        y_lim = [(y_max + y_min) / 2 - (y_max - y_min) * 0.6, (y_max + y_min) / 2 + (y_max - y_min) * 0.6]
        if y_lim[0] == y_lim[1]:
            y_lim[0] -= 0.5
            y_lim[1] += 0.5
        y_major, y_minor = MultipleLocator((y_lim[1] - y_lim[0]) / 5), MultipleLocator((y_lim[1] - y_lim[0]) / 25)

        ax.set_xlim(x_lim)
        ax.xaxis.set_major_locator(x_major)
        ax.xaxis.set_minor_locator(x_minor)

        ax.set_ylim(y_lim)
        ax.yaxis.set_major_locator(y_major)
        ax.yaxis.set_minor_locator(y_minor)

        ax1 = ax.twinx()
        ax1.set_ylim(y_lim)
        ax1.yaxis.set_major_locator(y_major)
        ax1.yaxis.set_minor_locator(y_minor)
        ax1.yaxis.set_major_formatter(plt.NullFormatter())

        ax2 = ax.twiny()
        ax2.set_xlim(x_lim)
        ax2.xaxis.set_major_locator(x_major)
        ax2.xaxis.set_minor_locator(x_minor)
        ax2.xaxis.set_major_formatter(plt.NullFormatter())

        plt.savefig(output_name + ".png")
        plt.close()

        # output docx file
        if self.docx_file:
            self.docx_file.add_fig(output_name + ".png", size, os.path.basename(output_name))

        return


class PlotBladed(QObject):
    """
    encapsulate plot Bladed result
    """

    one_file_finished = pyqtSignal(int)            # finish one file signal

    def __init__(self, var_file, filename, output_folder, size, out_docx=None):
        super(PlotBladed, self).__init__()

        self.var_file = var_file
        self.filename = filename
        self.output_folder = output_folder
        self.size = size
        self.docx_file = out_docx

        return

    def run(self):
        # output docx file
        if self.docx_file:
            self.docx_file.add_heading(self.filename, 1)

        bladed_res = load_result.BladedResult(self.var_file, self.filename)
        bladed_res.one_file_loaded.connect(self.one_file_loaded)
        # explicitly load the files
        bladed_res.load_results()

        order = bladed_res.get_order()
        res = bladed_res.get_result()

        # calculate output file name prefix
        file_prefix = os.path.join(self.output_folder, pf.remove_suffix_of_file(self.filename)) + "_"

        # pick out time history first
        time = None
        for key, val in res.items():
            if key.lower() == "time":
                time = res[key]
                break

        # plot the figures one by one
        for alias in order:
            if alias.lower() != "time":
                self.__plot(time, res[alias], self.size, file_prefix + alias)

                self.one_file_finished.emit(len(order) - 1)

        return

    def __plot(self, x: np.ndarray, y: np.ndarray, size, output_name):
        fig = plt.figure(figsize=size)
        plt.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.90)

        # skip some results and unit x and y size
        total_num = min(x.size, y.size)
        x, y = x[0: total_num], y[0: total_num]

        # plot
        ax = plt.subplot(111, label="GH-Bladed")
        ax.plot(x, y)
        ax.set_title(os.path.basename(output_name))

        # automatic limit
        x_lim = (np.min(x), np.max(x))
        if x_lim[0] == x_lim[1]:
            x_lim[0] -= 0.5
            x_lim[1] += 0.5
        x_major, x_minor = MultipleLocator((x_lim[1] - x_lim[0]) / 10), MultipleLocator((x_lim[1] - x_lim[0]) / 50)
        y_min, y_max = np.min(y), np.max(y)
        y_lim = [(y_max + y_min) / 2 - (y_max - y_min) * 0.6, (y_max + y_min) / 2 + (y_max - y_min) * 0.6]
        if y_lim[0] == y_lim[1]:
            y_lim[0] -= 0.5
            y_lim[1] += 0.5
        y_major, y_minor = MultipleLocator((y_lim[1] - y_lim[0]) / 5), MultipleLocator((y_lim[1] - y_lim[0]) / 25)

        ax.set_xlim(x_lim)
        ax.xaxis.set_major_locator(x_major)
        ax.xaxis.set_minor_locator(x_minor)

        ax.set_ylim(y_lim)
        ax.yaxis.set_major_locator(y_major)
        ax.yaxis.set_minor_locator(y_minor)

        ax1 = ax.twinx()
        ax1.set_ylim(y_lim)
        ax1.yaxis.set_major_locator(y_major)
        ax1.yaxis.set_minor_locator(y_minor)
        ax1.yaxis.set_major_formatter(plt.NullFormatter())

        ax2 = ax.twiny()
        ax2.set_xlim(x_lim)
        ax2.xaxis.set_major_locator(x_major)
        ax2.xaxis.set_minor_locator(x_minor)
        ax2.xaxis.set_major_formatter(plt.NullFormatter())

        plt.savefig(output_name + ".png")
        plt.close()

        # output docx file
        if self.docx_file:
            self.docx_file.add_fig(output_name + ".png", size, os.path.basename(output_name))

        return

    def one_file_loaded(self, num):
        self.one_file_finished.emit(num)


class PlotSpkBladed(QObject):
    """
        encapsulate plot and compare simpack and GH-Bladed results
    """

    one_file_finished = pyqtSignal(int)  # finish one file trigger

    def __init__(self, var_file_spk: str, file_spk: str, var_file_bladed: str, file_bladed: str, scale_for_spck: str,
                 output_folder: str, size: list, out_docx: docx_operation.DocxFile):
        super(PlotSpkBladed, self).__init__()

        self.var_file_spk = var_file_spk
        self.file_spk = file_spk
        self.var_file_bladed = var_file_bladed
        self.file_bladed = file_bladed
        self.scale_for_spck_file = scale_for_spck
        self.output_folder = output_folder
        self.size = size
        self.docx_file = out_docx

        #  simpack results scale factors
        self.scale_for_spck = dict()

        self.__sparse_scale_spck()

        return

    def __sparse_scale_spck(self):

        file = open(self.scale_for_spck_file, "r")

        # use total num to record how many lines are read
        for line in file.readlines():
            if line[0] == "#":
                # comment line
                continue
            elif line.strip() == "":
                # empty line
                continue
            else:
                # sparse the names
                names = [temp.strip() for temp in line.split("@")]

                if len(names) != 2:
                    # handle format error
                    raise Exception("Variable file {}: format wrong!".format(self.scale_for_spck_file))
                else:
                    # use list as the value of the dictionary
                    self.scale_for_spck[names[0]] = float(eval(names[1]))

        file.close()

    def run(self):
        # output docx file
        self.docx_file.add_heading(self.file_spk, 1)
        self.docx_file.add_heading(self.file_bladed, 1)

        # simpack result loading
        spk_res_ = load_result.SpkResult(self.var_file_spk, self.file_spk)
        spk_res, spk_order = spk_res_.get_result(), spk_res_.get_order()

        # bladed result loading
        bladed_res_ = load_result.BladedResult(self.var_file_bladed, self.file_bladed)
        bladed_res_.one_file_loaded.connect(self.one_file_loaded)
        # explicitly load the files
        bladed_res_.load_results()
        bladed_res, bladed_order = bladed_res_.get_result(), bladed_res_.get_order()

        # check they have the same aliases
        for alias in spk_order:
            if alias not in bladed_order:
                raise Exception("Aliases in Simpack and GH-Bladed variable files are not the same!")

        # calculate output file name prefix
        file_prefix = os.path.join(self.output_folder, "SPCK-{} @ BLADED-{}: ".format(
            pf.remove_suffix_of_file(self.file_spk),            # spck filename
            pf.remove_suffix_of_file(self.file_bladed)          # bladed filename
        ))

        # get time for both of them with 0 as the start
        time_spk = None
        for alias, value in spk_res.items():
            if alias.lower() == "time":
                time_spk = value - value[0]
                break
        time_bladed = None
        for alias, value in bladed_res.items():
            if alias.lower() == "time":
                time_bladed = value - value[0]
                break

        # plot figures one by one in the order of spck
        for alias in spk_order:
            if alias.lower() != "time":
                # scale simpack results to make them comparable
                ss = spk_res[alias] * self.scale_for_spck[alias] if alias in self.scale_for_spck.keys() else spk_res[alias]

                self.__plot(time_spk, ss, time_bladed, bladed_res[alias], self.size, file_prefix + alias)

                self.one_file_finished.emit(len(spk_order) - 1)

        return

    def __plot(self, spck_x, spck_y, bladed_x, bladed_y, size, output_name):
        fig = plt.figure(figsize=size)
        plt.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.90)

        # skip some results and unit x and y size
        total_num = min(min(spck_x.size, spck_y.size), min(bladed_x.size, bladed_y.size))
        spck_x, spck_y = spck_x[0: total_num], spck_y[0: total_num]
        bladed_x, bladed_y = bladed_x[0: total_num], bladed_y[0: total_num]

        # plot
        ax = plt.subplot(111, label="Simpack and GH-Bladed")
        ax.plot(spck_x, spck_y, "k-", linewidth=0.5, label="Simpack")
        ax.plot(bladed_x, bladed_y, "b--", linewidth=0.5, label="GH-Bladed")
        ax.set_title(os.path.basename(output_name))

        # automatic limit
        x_lim = (min(np.min(spck_x), np.min(bladed_x)), max(np.max(spck_x), np.max(bladed_x)))
        if x_lim[0] == x_lim[1]:
            x_lim[0] -= 0.5
            x_lim[1] += 0.5
        x_major, x_minor = MultipleLocator((x_lim[1] - x_lim[0]) / 10), MultipleLocator((x_lim[1] - x_lim[0]) / 50)
        y_min, y_max = min(np.min(spck_y), np.min(bladed_y)), max(np.max(spck_y), np.max(bladed_y))
        y_lim = [(y_max + y_min) / 2 - (y_max - y_min) * 0.6, (y_max + y_min) / 2 + (y_max - y_min) * 0.6]
        if y_lim[0] == y_lim[1]:
            y_lim[0] -= 0.5
            y_lim[1] += 0.5
        y_major, y_minor = MultipleLocator((y_lim[1] - y_lim[0]) / 5), MultipleLocator((y_lim[1] - y_lim[0]) / 25)

        ax.set_xlim(x_lim)
        ax.xaxis.set_major_locator(x_major)
        ax.xaxis.set_minor_locator(x_minor)

        ax.set_ylim(y_lim)
        ax.yaxis.set_major_locator(y_major)
        ax.yaxis.set_minor_locator(y_minor)

        ax1 = ax.twinx()
        ax1.set_ylim(y_lim)
        ax1.yaxis.set_major_locator(y_major)
        ax1.yaxis.set_minor_locator(y_minor)
        ax1.yaxis.set_major_formatter(plt.NullFormatter())

        ax2 = ax.twiny()
        ax2.set_xlim(x_lim)
        ax2.xaxis.set_major_locator(x_major)
        ax2.xaxis.set_minor_locator(x_minor)
        ax2.xaxis.set_major_formatter(plt.NullFormatter())

        ax.legend(ncol=2, loc="lower right", frameon=False)

        plt.savefig(output_name + ".png")
        plt.close()

        # output docx and some important metrics
        max_spk, max_bladed = round(np.max(spck_y), 10), round(np.max(bladed_y), 10)
        err_max = round(abs(max_spk - max_bladed) / max(abs(max_spk), abs(max_bladed)) * 100, 10)
        min_spk, min_bladed = round(np.min(spck_y), 10), round(np.min(bladed_y), 10)
        err_min = round(abs(min_spk - min_bladed) / max(abs(min_spk), abs(min_bladed)) * 100, 10)
        bar_spk, bar_bladed = round(np.mean(spck_y), 10), round(np.mean(bladed_y), 10)
        err_bar = round(abs(bar_spk - bar_bladed) / max(abs(bar_spk), abs(bar_bladed)) * 100, 10)
        std_spk, std_bladed = round(np.std(spck_y), 10), round(np.std(bladed_y), 10)
        err_std = round(abs(std_spk - std_bladed) / max(abs(std_spk), abs(std_bladed)) * 100, 10)
        Cr = round(np.sum((spck_y - bar_spk) * (bladed_y - bar_bladed)) / std_spk / std_bladed / total_num * 100, 10)
        Ca = (np.sum(spck_y ** 2) / np.sum(bladed_y ** 2)) ** 0.5
        Ca = round(100 / Ca if Ca > 1 else Ca * 100, 10)
        # output
        table = [
            [" ", "Simpack", "GH-Bladed", "Error"],
            ["Min", min_spk, min_bladed, err_min],
            ["Max", max_spk, max_bladed, err_max],
            ["Mean", bar_spk, bar_bladed, err_bar],
            ["Std", std_spk, std_bladed, err_std],
            ["Phase error", " ", " ", Cr],
            ["Amplitude error", " ", " ", Ca]
        ]
        self.docx_file.add_fig(output_name + ".png", size, os.path.basename(output_name))
        self.docx_file.add_table(table)
        self.docx_file.add_para("    ")

        return

    def one_file_loaded(self, num):
        self.one_file_finished.emit(num)


if __name__ == "__main__":
    # pthread = PlotSpk("./resources/alias_name_spk.txt", "./data/012_results/012_003.txt", "./data/012_results", (8, 4), None)
    # pthread.run()

    # pthread = PlotBladed("resources/alias_name_bladed.txt", "./data/19/powprodWT1-19.$PJ", "./data/19/", (8, 4))
    # pthread.run()

    pthread = PlotSpkBladed("./resources/alias_name_spk.txt", "./data/012_results/012_019.txt",
                            "./resources/alias_name_bladed.txt", "./data/19/powprodWT1-19.$PJ",
                            "./resources/scale_factors_spk.txt", "./data/", [8, 4],
                            docx_operation.DocxFile("./data/Spck_bladed"))
    pthread.run()
