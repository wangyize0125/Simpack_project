# -*-coding:utf-8 -*-
# @Time    : 2021/7/4 12:50 上午
# @Author  : Yize Wang
# @File    : load_spk_result.py
# @Software: PyCharm

import os
import logging
import numpy as np


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

    def get_page_sets(self):
        return self.__page_sets


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    spk_res = SpkResult("./data/012_results/012_003.txt")

    print(spk_res.get_spk_res_file())
    print(spk_res.get_page_sets())

    print(spk_res.time[0])
    print(spk_res.pitch_blade[0][0])
    print(spk_res.pitch_blade[1][0])
    print(spk_res.pitch_blade[2][0])
    print(spk_res.generator_speed[0])
    print(spk_res.generator_torque[0])
    for i in range(3):
        for j in range(6):
            print(spk_res.blade_force[i][j][0])
    for j in range(6):
        print(spk_res.tower_btm_force[j][0])
    for j in range(6):
        print(spk_res.tower_top_force[j][0])
