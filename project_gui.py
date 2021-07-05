# -*-coding:utf-8 -*-
# @Time    : 2021/7/4 12:15 下午
# @Author  : Yize Wang
# @File    : project_gui.py
# @Software: PyCharm

import sys
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtGui import QIcon

import images_qr
import app_constants
from main_tabs import MainTab


class SpkProj(QMainWindow):
    """
    main window
    """

    def __init__(self, constants):
        super(SpkProj, self).__init__()

        # window title
        self.setWindowTitle(constants.app_name)
        # window icon
        self.setWindowIcon(QIcon(":resources/logo.ico"))

        # resize the window, for convenience, the size is fixed
        geom = QApplication.desktop().screenGeometry()
        width, height = geom.width(), geom.height()
        self.setFixedSize(int(width * constants.window_size), int(height * constants.window_size))

        # move to center
        self.move((width - self.width()) // 2, (height - self.height()) // 2)

        # status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # widgets
        self.main_tab = MainTab(self, constants.tab_size)
        self.main_tab.finish.connect(self.finish_bar)

        return

    def finish_bar(self, software):
        self.status_bar.showMessage("Plot figures for {} finished!    Finished time: {}".format(software, datetime.datetime.now()))

        return


if __name__ == "__main__":
    # initialize an application instance
    app = QApplication(sys.argv)

    app_gui = SpkProj(app_constants)
    app_gui.show()

    # hook up the current application
    sys.exit(app.exec_())
