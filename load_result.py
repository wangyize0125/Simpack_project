# -*-coding:utf-8 -*-
# @Time    : 2021/7/4 12:50 上午
# @Author  : Yize Wang
# @File    : load_result.py
# @Software: PyCharm

import os
import re
import logging
import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject

import public_functions as pf


class SpkResult:
    """
    This class encapsulate the numerical simulation results from Simpack (in later development of these codes, it is
    simply called Spk). Users can access the attribute of this class to attain the simulation results

    The simulation results are (include but not only have these):
    1. Pitch angle of each blade as function of time
    2. Generator torque as function of time
    3. Rotor speed as function of time
    4. Blade root force as function of time (fx, fy, fz, mx, my, mz)
    5. Tower top forces as function of time (fx, fy, fz, mx, my, mz)
    6. Tower bottom forces as function of time (fx, fy, fz, mx, my, mz)
    """

    NUM_PAGE = 15
    IDX_TIME = 0
    IDX_PITCH = 1
    IDX_GENER_SPD = 7
    IDX_GENER_TRQ = 9
    IDX_BLADE_FRC = 11
    IDX_TWR_B_FRC = 23
    IDX_TWR_T_FRC = 27
    IDX_BLADE_TRQ = 31
    IDX_TWR_B_TRQ = 43
    IDX_TWR_T_TRQ = 47
    NUM_FIGURE = 35

    def __init__(self, spk_res_file: str):
        # record the filename
        self.__spk_res_file = spk_res_file

        # record the page sets in this file
        self.__page_sets = None

        # time
        self.time = None

        # pitch angle of each blade
        self.pitch_blade = [None, None, None]

        # generator speed
        self.generator_speed = None

        # generator torque
        self.generator_torque = None

        # used for indexing the forces in following arrays
        self.forces = ["fx", "fy", "fz", "mx", "my", "mz"]

        # blade root forces
        self.blade_force = [
            [None, None, None, None, None, None],
            [None, None, None, None, None, None],
            [None, None, None, None, None, None]
        ]

        # tower bottom force
        self.tower_btm_force = [None, None, None, None, None, None]

        # tower top forces
        self.tower_top_force = [None, None, None, None, None, None]

        # load result file
        self.__load(spk_res_file)

    def __load(self, spk_res_file):
        # check whether the file exists
        if not os.path.exists(spk_res_file):
            raise Exception("File: {} does not exist!".format(spk_res_file))

        # start loading
        logging.info("Loading spk result file: {}".format(spk_res_file))

        file = open(spk_res_file, "r")
        logging.info("Projection name: {}".format(file.readline().strip().replace("\"", "")))
        logging.info("Page sets: "); file.readline()

        # all page sets in this file
        page_sets = [page_set.replace("\"", "") for page_set in file.readline().split()]
        # check the number of page sets
        if len(page_sets) is not self.NUM_PAGE:
            raise Exception("Number of page sets wrong in this file: {}".format(spk_res_file))
        else:
            self.__page_sets = page_sets
        # display page sets' name for debug
        for page in range(self.NUM_PAGE):
            logging.info("\t\t{}. {}".format(page + 1, page_sets[page]))

        # skip diagram, legend, and unit lines
        file.readline(); file.readline(); file.readline()

        # load data
        data = np.array([[float(var) for var in line.split("\t")] for line in file.readlines()])

        # assign data
        # time
        self.time = data[:, self.IDX_TIME]

        # pitch angle of the blades
        for blade_id in range(3):
            self.pitch_blade[blade_id] = data[:, self.IDX_PITCH + blade_id * 2]

        # generator torque
        self.generator_torque = data[:, self.IDX_GENER_TRQ]

        # generator speed
        self.generator_speed = data[:, self.IDX_GENER_SPD]

        # blade root forces
        for blade_id in range(3):
            for force_id in range(3):
                self.blade_force[blade_id][force_id] = data[:, self.IDX_BLADE_FRC + blade_id * 4 + force_id]

        # tower bottom forces
        for force_id in range(3):
            self.tower_btm_force[force_id] = data[:, self.IDX_TWR_B_FRC + force_id]

        # tower top force
        for force_id in range(3):
            self.tower_top_force[force_id] = data[:, self.IDX_TWR_T_FRC + force_id]

        # blade root torques
        for blade_id in range(3):
            for torque_id in range(3, 6):
                self.blade_force[blade_id][torque_id] = data[:, self.IDX_BLADE_TRQ + blade_id * 4 + torque_id - 3]

        # tower bottom forces
        for torque_id in range(3, 6):
            self.tower_btm_force[torque_id] = data[:, self.IDX_TWR_B_TRQ + torque_id - 3]

        # tower top force
        for torque_id in range(3, 6):
            self.tower_top_force[torque_id] = data[:, self.IDX_TWR_T_TRQ + torque_id - 3]

        file.close()

    def get_spk_res_file(self):
        return self.__spk_res_file

    def get_page_sets(self) -> dict:
        return self.__page_sets


class BladedResult(QObject):
    """
    This class encapsulate the numerical simulation results from GH-Bladed (in later development of these codes, it is
    simply called Bladed). Users can access the attribute (result: dict) of this class to attain the simulation results

    owing to that there are so many files needing to be loaded, this class is inherited from QObject so that it can emit
    a signal when one file is loaded, and the parent Qt object can handle the corresponding signal to process GUI
    """

    # in bladed result file, the result starts with these keywords
    var_line_start_with = "VARIAB"
    dim_line_start_with = "DIMENS"
    axis_val_start_with = "AXIVAL"

    # when one file is loaded, this signal is emitted
    one_file_loaded = pyqtSignal(int)

    def __init__(self, var_list_file: str, res_file: str):
        super(BladedResult, self).__init__()

        # record the filename
        self.__res_file = res_file

        # record the folder of the result file
        self.__res_folder = os.path.dirname(self.__res_file)

        # record the variable list filename
        self.__var_list_file = var_list_file

        # use a dictionary to store the variables (value) and the alias of the variables (key)
        self.__alias_and_name = dict()

        # use a set to store the requested variables
        self.requested_variables = set()

        # use a dictionary to store the position (value) and the real variables (key)
        self.name_and_position = dict()

        # record the results files
        self.__res_file_list = []

        # record the files need to be loaded (key) and their corresponding alias (value)
        self.load_file_and_alias = dict()
        # record the files need to be loaded (key) and their corresponding steps (value)
        self.load_file_and_step = dict()

        # use a dictionary to store the position of the alias (value) and the alias of the variables (key)
        self.__alias_and_pos = dict()

        # use a dictionary to store the values (value) and the alias of the variables (key)
        self.__alias_and_value = dict()

        # load the results
        self.__load()

        return

    def __load(self):
        # sparse the alias and name file first
        self.__sparse_alias_name()

        # sparse all the result variables in this folder
        self.__sparse_name_position()

        # sparse axial position of the results
        self.__sparse_alias_pos()
        print(self.load_file_and_step)
        print(self.__alias_and_pos)
        return

    def __sparse_alias_name(self):
        """
        sparse the alias and name of the variables
        sparse the requested variables storing the real names
        check whether time is requested
        """

        file = open(self.__var_list_file, "r")

        # use total num to record how many lines are read
        total_num = 0
        for line in file.readlines():
            if line[0] == "#":
                # comment line
                continue
            elif line.strip() == "":
                # empty line
                continue
            else:
                # sparse the names
                names = [temp.strip() for temp in line.split(":")]

                if len(names) != 3:
                    # handle format error
                    raise Exception("Variable file {}: format wrong!".format(self.__var_list_file))
                else:
                    # use list as the value of the dictionary
                    self.__alias_and_name[names[0]] = [names[1], names[2]]

                    # successfully add a record
                    total_num += 1

        file.close()

        # if total_num != len(dict), same lines!, which is illegal!
        if total_num != len(self.__alias_and_name):
            raise Exception("Same lines in file {}".format(self.__var_list_file))

        # get the requested variables
        self.requested_variables = set([val[0] for key, val in self.__alias_and_name.items()])

        # check time is requested
        time_requested_flag = False
        for temp_var in self.__alias_and_name.keys():
            if temp_var.lower() == "time":
                time_requested_flag = True
                break
        if not time_requested_flag:
            raise Exception("You must include a [Time] variable in {}".format(self.__var_list_file))

        return

    def __sparse_name_position(self):
        """
        sparse name and its corresponding position
        sparse load file and aliases
        """

        # get the filename without suffix of the project
        filename_without_suffix = pf.remove_suffix_of_file(self.__res_file)

        # find all the result files under this folder with the same filename
        all_file_list = os.listdir(self.__res_folder)
        for file in all_file_list:
            if os.path.isfile(os.path.join(self.__res_folder, file)):
                if file.startswith(filename_without_suffix):
                    if file.split(".")[-1][0] == "%":
                        self.__res_file_list.append(os.path.join(self.__res_folder, file))
                    else:
                        continue
                else:
                    continue
            else:
                continue

        # sparse the position of the requested variable
        for filename in self.__res_file_list:
            file = open(filename, "r")

            # find the variable name line start with VARIAB
            for line in file.readlines():
                if line.startswith(self.var_line_start_with):
                    # successfully find the variables
                    vars_in_line = self.sparse_vars(line)

                    # check each variables whether they are requested
                    for temp_var in vars_in_line:
                        if temp_var in self.requested_variables:
                            # remove the temp var from the requested variables
                            self.requested_variables.remove(temp_var)

                            # record position of this requested variable
                            self.name_and_position[temp_var] = [filename, vars_in_line.index(temp_var)]

                    # handle all of the variables in this file and break out
                    break

            # if all the requested variables are found, break the loop
            if not self.requested_variables:
                break

        # find out which files should be loaded
        need_load_files = list(set([val[0] for key, val in self.name_and_position.items()]))
        for i in range(len(need_load_files)):
            self.load_file_and_alias[need_load_files[i]] = []
        for alias, name in self.__alias_and_name.items():
            self.load_file_and_alias[self.name_and_position[name[0]][0]].append(alias)

        return

    def sparse_vars(self, line: str) -> list:
        # remove the start with string at the head of line
        back_up = list(line.replace(self.var_line_start_with, "").strip())

        # use "\n" to substitute " " between two "'" symbol
        i, total_num = -1, len(back_up)
        while i < total_num - 1:
            i = i + 1

            if back_up[i] == "'":
                # start substitution
                while i < total_num:
                    i = i + 1

                    if back_up[i] == " ":
                        # substitute
                        back_up[i] = "\n"
                    elif back_up[i] == "'":
                        # end
                        break
                    else:
                        continue
            else:
                continue

        # now we can split the line using "'" and "
        back_up = "".join(back_up)
        raw_vars = re.split(r"'| ", back_up)

        # post process to remove empty strings and change "\n" back to " ", and remove space at both sides of the names
        variables = []
        for temp_var in raw_vars:
            if temp_var.strip() != "":
                variables.append(temp_var.replace("\n", " ").strip())

        return variables

    def __sparse_alias_pos(self):
        for filename, aliases in self.load_file_and_alias.items():
            file = open(filename, "r")

            # check how many dimensions of the results
            for line in file.readlines():
                if line.startswith(self.dim_line_start_with):
                    # sparse the dimension line
                    line = line.replace(self.dim_line_start_with, "")
                    dims = [int(item) for item in line.split()]

                    break

            file.close()

            # determine the steps according to dims
            if len(dims) == 2:
                # 2 dimension, the axial index = 0
                for alias in aliases:
                    self.__alias_and_pos[alias] = self.name_and_position[self.__alias_and_name[alias][0]] + [int(0)]

                # record the step when load this file
                self.load_file_and_step[filename] = int(1)
            elif len(dims) == 3:
                # reopen the file
                file = open(filename, "r")
                axial_coordinates = []
                # check the axial position of the results
                for line in file.readlines():
                    if line.startswith(self.axis_val_start_with):
                        # sparse the axial coordinates of this file
                        line = line.replace(self.axis_val_start_with, "")
                        axial_coordinates = np.array([float(item) for item in line.split()])

                        break
                file.close()

                for alias in aliases:
                    # the nearest one is output
                    dist = np.abs(axial_coordinates - float(self.__alias_and_name[alias][1]))
                    self.__alias_and_pos[alias] = self.name_and_position[self.__alias_and_name[alias][0]] + [int(np.argmin(dist))]

                # record the step when load this file
                self.load_file_and_step[filename] = int(dims[1])
            else:
                raise Exception("The format of the bladed file is unknown. Please contact the developer!")

        return

    def get_result(self) -> dict:
        # load all the requested variables
        self.__load_results()

        return self.__alias_and_value

    def __load_results(self):
        # loop for each file need to be loaded
        for filename, aliases in self.load_file_and_alias.items():
            t_d = np.loadtxt(filename.replace("%", "$"))

            self.one_file_loaded.emit(len(self.load_file_and_alias))

            for alias in aliases:
                pos = self.__alias_and_pos[alias]

                self.__alias_and_value[alias] = t_d[pos[2]::self.load_file_and_step[filename], pos[1]]
        return


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    #
    # spk_res = SpkResult("./data/012_results/012_003.txt")
    #
    # print(spk_res.get_spk_res_file())
    # print(spk_res.get_page_sets())
    #
    # print(spk_res.time[0])
    # print(spk_res.pitch_blade[0][0])
    # print(spk_res.pitch_blade[1][0])
    # print(spk_res.pitch_blade[2][0])
    # print(spk_res.generator_speed[0])
    # print(spk_res.generator_torque[0])
    # for i in range(3):
    #     for j in range(6):
    #         print(spk_res.blade_force[i][j][0])
    # for j in range(6):
    #     print(spk_res.tower_btm_force[j][0])
    # for j in range(6):
    #     print(spk_res.tower_top_force[j][0])

    bld_res = BladedResult("resources/alias_name.txt", "./data/19/powprodWT1-19.$PJ")

