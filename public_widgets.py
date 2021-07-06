# -*-coding:utf-8 -*-
# @Time    : 2021/7/4 6:41 下午
# @Author  : Yize Wang
# @File    : public_widgets.py
# @Software: PyCharm

from PyQt5.QtWidgets import QMessageBox, QWidget


class ErrBox(QMessageBox):
    def __init__(self, parent: QWidget, msg):
        super(MsgBox, self).__init__()

        self.setFixedSize(parent.width() * 0.8, parent.height() * 0.4)
        self.move((parent.width() - self.width()) // 2, (parent.height() - self.height()) // 2)

        QMessageBox.critical(self, "Error", msg)

        return


class MsgBox(QMessageBox):
    def __init__(self, parent: QWidget, msg):
        super(MsgBox, self).__init__()

        self.setFixedSize(parent.width() * 0.8, parent.height() * 0.4)
        self.move((parent.width() - self.width()) // 2, (parent.height() - self.height()) // 2)

        QMessageBox.critical(self, "Tip", msg)

        return
