# -*-coding:utf-8 -*-
# @Time    : 2021/7/4 6:41 下午
# @Author  : Yize Wang
# @File    : public_widgets.py
# @Software: PyCharm

from PyQt5.QtWidgets import QMessageBox, QWidget, QDialog, QLabel, QLineEdit, QPushButton
from PyQt5 import QtGui


class ErrBox(QMessageBox):
    def __init__(self, parent: QWidget, msg):
        super(ErrBox, self).__init__()

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


class FatigueAnalysis(QDialog):
    """
    define the weibull distributions and auto wind speed fill in
    """

    default_C = 2 * 7.4 / (3.1415926535 ** 0.5 / 2)
    default_K = 2

    def __init__(self, parent=None, size=(600, 400)):
        super(FatigueAnalysis, self).__init__(parent)

        # size and position settings
        self.setFixedSize(*size)
        self.move(int((parent.width() - self.width()) / 2), int((parent.height() - self.height()) / 2))

        self.C = None
        self.K = None

        self.label_scale_factor = QLabel(self)
        self.label_shape_factor = QLabel(self)
        self.l_scale_factor = QLineEdit(self)
        self.l_shape_factor = QLineEdit(self)
        self.btn_yes = QPushButton(self)
        self.btn_no = QPushButton(self)

        self.ui_settings()

        return

    def ui_settings(self):
        y_pos = self.height() * 0.1

        self.label_scale_factor.setText("Weibull scale factor: ")
        self.label_scale_factor.setFixedSize(self.width() * 0.46, self.label_scale_factor.height())
        self.label_scale_factor.move(self.width() * 0.02, y_pos)

        self.l_scale_factor.setPlaceholderText("Use default: {}".format(self.default_C))
        self.l_scale_factor.setFixedSize(self.width() * 0.46, self.l_scale_factor.height())
        self.l_scale_factor.move(self.width() * 0.52, y_pos)
        self.l_scale_factor.setValidator(QtGui.QDoubleValidator())

        y_pos += self.l_scale_factor.height() * 1.2

        self.label_shape_factor.setText("Weibull shape factor: ")
        self.label_shape_factor.setFixedSize(self.width() * 0.46, self.label_shape_factor.height())
        self.label_shape_factor.move(self.width() * 0.02, y_pos)

        self.l_shape_factor.setPlaceholderText("Use default: {}".format(self.default_K))
        self.l_shape_factor.setFixedSize(self.width() * 0.46, self.l_shape_factor.height())
        self.l_shape_factor.move(self.width() * 0.52, y_pos)
        self.l_shape_factor.setValidator(QtGui.QDoubleValidator())

        y_pos += self.l_shape_factor.height() * 1.2
        self.btn_yes.setText("Yes")
        self.btn_yes.setFixedSize(self.width() * 0.46, self.btn_yes.height())
        self.btn_yes.move(self.width() * 0.02, y_pos)
        self.btn_yes.clicked.connect(self.yes)

        self.btn_no.setText("No")
        self.btn_no.setFixedSize(self.width() * 0.46, self.btn_no.height())
        self.btn_no.move(self.width() * 0.52, y_pos)
        self.btn_no.clicked.connect(self.no)

        return

    def yes(self):
        # record the values
        self.C = float(self.l_scale_factor.text()) if self.l_scale_factor.text() else self.default_C
        self.K = float(self.l_shape_factor.text()) if self.l_shape_factor.text() else self.default_K

        self.close()

        return

    def no(self):
        # record the values
        self.C, self.K = None, None

        self.close()

        return

