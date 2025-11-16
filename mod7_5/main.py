# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
import sys
import system
from laws import UniformDistributionLaw, ConstantDistributionLaw

UI_MAINWINDOW_PATH = "./mod7_5/ui/mainWindow.ui"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = uic.loadUi(UI_MAINWINDOW_PATH, self)
        
        # Инициализация системы с начальными параметрами
        self.system = None
        self.method = "events"  # По умолчанию событийный метод
        
        self.connect_buttons()
        self.update_system_parameters()

    def connect_buttons(self):
        self.ui.modeling_btn.clicked.connect(self.modeling)

    # def initialize_system(self):
    #     try:
    #         # Получение параметров из интерфейса
    #         client_avg = self.ui.client_spb.value()
    #         client_delta = self.ui.client_delta_spb.value()
            
    #         op1_avg = self.ui.op1_spb.value()
    #         op1_delta = self.ui.op1_delta_spb.value()
            
    #         op2_avg = self.ui.op2_spb.value()
    #         op2_delta = self.ui.op2_delta_spb.value()
            
    #         op3_avg = self.ui.op3_spb.value()
    #         op3_delta = self.ui.op3_delta_spb.value()
            
    #         comp1_const = self.ui.comp1_spb.value()
    #         comp2_const = self.ui.comp2_spb.value()
            
    #         n = self.ui.n_spb.value()
            
    #         # Создание системы с начальными параметрами
    #         self.system = system.System(
    #             client_law=UniformDistributionLaw(a=client_avg-client_delta, b=client_avg+client_delta),
    #             op1_law=UniformDistributionLaw(a=op1_avg-op1_delta, b=op1_avg+op1_delta),
    #             op2_law=UniformDistributionLaw(a=op2_avg-op2_delta, b=op2_avg+op2_delta),
    #             op3_law=UniformDistributionLaw(a=op3_avg-op3_delta, b=op3_avg+op3_delta),
    #             comp1_law=ConstantDistributionLaw(c=comp1_const),
    #             comp2_law=ConstantDistributionLaw(c=comp2_const),
    #             n=n, dt=1, method=self.method
    #         )
            
    #     except Exception as e:
    #         self.show_error(f"Ошибка инициализации системы: {str(e)}")

    def modeling(self):
        try:
            self.update_system_parameters()
            result = self.system.calculate()
            self.display_results(result)
            
        except Exception as e:
            self.show_error(f"Ошибка при моделировании: {str(e)}")

    def update_system_parameters(self):
        try:
            client_avg = self.ui.client_spb.value()
            client_delta = self.ui.client_delta_spb.value()
            
            op1_avg = self.ui.op1_spb.value()
            op1_delta = self.ui.op1_delta_spb.value()
            
            op2_avg = self.ui.op2_spb.value()
            op2_delta = self.ui.op2_delta_spb.value()
            
            op3_avg = self.ui.op3_spb.value()
            op3_delta = self.ui.op3_delta_spb.value()
            
            comp1_const = self.ui.comp1_spb.value()
            comp2_const = self.ui.comp2_spb.value()
            
            n = self.ui.n_spb.value()
            
            self.system = system.System(
                client_law=UniformDistributionLaw(a=client_avg-client_delta, b=client_avg+client_delta),
                op1_law=UniformDistributionLaw(a=op1_avg-op1_delta, b=op1_avg+op1_delta),
                op2_law=UniformDistributionLaw(a=op2_avg-op2_delta, b=op2_avg+op2_delta),
                op3_law=UniformDistributionLaw(a=op3_avg-op3_delta, b=op3_avg+op3_delta),
                comp1_law=ConstantDistributionLaw(c=comp1_const),
                comp2_law=ConstantDistributionLaw(c=comp2_const),
                n=n, dt=1, method=self.method
            )
            
        except ValueError as e:
            raise ValueError(f"Некорректные значения параметров: {str(e)}")
        except Exception as e:
            raise Exception(f"Ошибка обновления параметров: {str(e)}")

    def display_results(self, result):
        try:
            self.ui.processed_count_line_edit.setText(str(result['processed_count']))
            self.ui.rejected_count_line_edit.setText(str(result['rejected_count']))
            
            total_requests = result['generated_count'] + result['rejected_count']
            if total_requests > 0:
                rejection_probability = result['rejected_count'] / total_requests
                self.ui.rejected_probability_line_edit.setText(f"{rejection_probability:.4f}")
            else:
                self.ui.rejected_probability_line_edit.setText("0.0000")
                
        except Exception as e:
            self.show_error(f"Ошибка отображения результатов: {str(e)}")

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Ошибка")
        msg.setInformativeText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec_()

    def closeEvent(self, event):
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
