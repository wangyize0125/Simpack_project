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
            self.docx_file.add_heading(os.path.basename(self.filename), 1)

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
            self.docx_file.add_heading(pf.remove_suffix_of_file(self.filename), 1)

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


if __name__ == "__main__":
    # pthread = PlotSpk("./resources/alias_name_spk.txt", "./data/012_results/012_003.txt", "./data/012_results", (8, 4), None)
    # pthread.run()

    pthread = PlotBladed("resources/alias_name_bladed.txt", "./data/19/powprodWT1-19.$PJ", "./data/19/", (8, 4))
    pthread.run()