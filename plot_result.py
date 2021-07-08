# -*-coding:utf-8 -*-
# @Time    : 2021/7/4 5:00 下午
# @Author  : Yize Wang
# @File    : plot_result.py
# @Software: PyCharm

import os
import re
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtGui
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

    def __init__(self, filename: str, output_folder: str, size: list, out_docx: docx_operation.DocxFile):
        super(PlotSpk, self).__init__()

        self.filename = filename
        self.output_folder = output_folder
        self.size = size

        self.docx_file = out_docx

        return

    def run(self):
        # output docx file
        if self.docx_file:
            self.docx_file.add_heading(os.path.basename(self.filename), 1)

        spk_res = load_result.SpkResult(self.filename)

        # calculate output file name prefix
        file_prefix = os.path.basename(self.filename)  # project filename
        file_prefix = ".".join(file_prefix.split(".")[0: -1])  # remove extension
        file_prefix = os.path.join(self.output_folder, file_prefix)  # all prefix of the filenames

        # pitch angle of blades
        for blade_id in range(3):
            self.__plot(spk_res.time, spk_res.pitch_blade[blade_id], self.size,
                        file_prefix + "_Pitch_blade_{}".format(blade_id + 1))
            self.one_file_finished.emit(spk_res.NUM_FIGURE)

        # generator torque
        self.__plot(spk_res.time, spk_res.generator_torque, self.size, file_prefix + "_Generator_torque")
        self.one_file_finished.emit(spk_res.NUM_FIGURE)

        # generator speed
        self.__plot(spk_res.time, spk_res.generator_speed, self.size, file_prefix + "_Generator_speed")
        self.one_file_finished.emit(spk_res.NUM_FIGURE)

        # blade force
        for blade_id in range(3):
            for force_id in range(6):
                self.__plot(spk_res.time, spk_res.blade_force[blade_id][force_id], self.size,
                            file_prefix + "_Blade_{}_{}".format(blade_id + 1, spk_res.forces[force_id]))
                self.one_file_finished.emit(spk_res.NUM_FIGURE)

        # tower bottom force
        for force_id in range(6):
            self.__plot(spk_res.time, spk_res.tower_btm_force[force_id], self.size,
                        file_prefix + "_Tower_btm_{}".format(spk_res.forces[force_id]))
            self.one_file_finished.emit(spk_res.NUM_FIGURE)

        # tower top force
        for force_id in range(6):
            self.__plot(spk_res.time, spk_res.tower_top_force[force_id], self.size,
                        file_prefix + "_Tower_top_{}".format(spk_res.forces[force_id]))
            self.one_file_finished.emit(spk_res.NUM_FIGURE)

        return

    def __plot(self, x: np.ndarray, y: np.ndarray, size, output_name):
        fig = plt.figure(figsize=size)
        plt.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.90)

        # plot
        ax = plt.subplot(111, label="Simpack")
        ax.plot(x, y)
        ax.set_title(re.split('/', output_name)[-1])

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
            self.docx_file.add_fig(output_name + ".png", size, output_name.split("/")[-1])

        return


class PlotBladed(QObject):
    """
    encapsulate plot Bladed result
    """

    one_file_finished = pyqtSignal(int)            # finish one file signal

    def __init__(self, var_list_file, filename, output_folder, size, out_docx=None):
        super(PlotBladed, self).__init__()

        self.var_list_file = var_list_file
        self.filename = filename
        self.output_folder = output_folder
        self.size = size

        self.docx_file = out_docx

        return

    def run(self):
        # output docx file
        if self.docx_file:
            self.docx_file.add_heading(pf.remove_suffix_of_file(self.filename), 1)

        bladed_res = load_result.BladedResult(self.var_list_file, self.filename)
        bladed_res.one_file_loaded.connect(self.one_file_loaded)
        bladed_res = bladed_res.get_result()

        # calculate output file name prefix
        file_prefix = os.path.join(self.output_folder, pf.remove_suffix_of_file(self.filename)) + "_"

        # pick out time history first
        time = None
        for key, val in bladed_res.items():
            if key.lower() == "time":
                time = bladed_res[key]
                break

        # plot the figures one by one
        for key, val in bladed_res.items():
            if key.lower() != "time":
                self.__plot(time, bladed_res[key], self.size, file_prefix + key)

                self.one_file_finished.emit(len(bladed_res) - 1)

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
            self.docx_file.add_fig(output_name + ".png", size, output_name.split("/")[-1])

        return

    def one_file_loaded(self, num):
        self.one_file_finished.emit(num)


if __name__ == "__main__":
    # pthread = PlotSpk("./data/012_results/012_003.txt", "./data/012_results", (8, 4), None)
    # pthread.run()

    pthread = PlotBladed("./resources/alias_name.txt", "./data/19/powprodWT1-19.$PJ", "./data/19/", (8, 4))
    pthread.run()
