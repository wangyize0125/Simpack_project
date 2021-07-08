# -*-coding:utf-8 -*-
# @Time    : 2021/7/7 2:43 下午
# @Author  : Yize Wang
# @File    : public_functions.py
# @Software: PyCharm

import os


def remove_suffix_of_file(filename: str) -> str:
    filename_without_suffix = ".".join(os.path.basename(filename).split(".")[0:-1])

    return filename_without_suffix


if __name__ == '__main__':
    print(remove_suffix_of_file("1.1.1.1.txt"))
