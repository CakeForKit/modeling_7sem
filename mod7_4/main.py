from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog
import sys
import modeller
from choose_distribution import ChooseDistribution

UI_MAINWINDOW_PATH = "./mod7_4/ui/main_window.ui"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = uic.loadUi(UI_MAINWINDOW_PATH, self)
        self.connect_buttons()
        self.fill_method_combobox()

        self.modeling_method = 0    # index - ["Принцип ∆t", "Событийный принцип"]
        self.generator_generator = None
        self.processor_generator = None

    def connect_buttons(self):
        self.choose_generator_btn.clicked.connect(self.choose_generator_ditribution)
        self.ui.choose_processor_btn.clicked.connect(self.choose_processor_distribution)
        self.ui.method_comboBox.currentIndexChanged.connect(self.on_method_changed)
        self.modeling_btn.clicked.connect(self.modeling)

    def modeling(self):
        self.statusBar().showMessage("")
        if self.generator_generator is None:
            self.statusBar().showMessage("Ошибка: нужно выбрать распределение генератора заявок")
            return
        if self.processor_generator is None:
            self.statusBar().showMessage("Ошибка: нужно выбрать распределение обслуживающего аппарата")
            return
                
        cnt_requests = self.cnt_requests_spb.value()
        percent_dup_requests = self.percent_dup_requests.value()
        self.modeling_method = self.ui.method_comboBox.currentIndex()

        model = modeller.Modeller(
            self.generator_generator, 
            self.processor_generator, 
            percent_dup_requests)
        
        if self.modeling_method == 0:
            delta_t = self.t_spb.value()
            processed_requests, reentered_requests, max_queue_size, current_time = model.time_based_modelling(cnt_requests, delta_t)
            # print(f"processed_requests={processed_requests}, reentered_requests={reentered_requests}, max_queue_size={max_queue_size}, current_time={current_time}")
        else:
            processed_requests, reentered_requests, max_queue_size, proc_period = model.event_based_modelling(cnt_requests)
            # print(f"processed_requests={processed_requests}, reentered_requests={reentered_requests}, max_queue_size={max_queue_size}, proc_period={proc_period}")
        self.display_results(processed_requests, reentered_requests, max_queue_size)

    def display_results(self, processed_requests, reentered_requests, max_queue_size):
        self.ui.cnt_proc_requests.setText(str(processed_requests))
        self.ui.cnt_dub_proc_requests.setText(str(reentered_requests))
        self.ui.max_queue_length.setText(str(max_queue_size))

    def fill_method_combobox(self):
        methods = ["Принцип ∆t", "Событийный принцип"]
        self.ui.method_comboBox.clear()  
        self.ui.method_comboBox.addItems(methods)
    
    def on_method_changed(self, index):
        if index == 0:  # "Принцип ∆t" - первый элемент (индекс 0)
            self.ui.t_spb.setEnabled(True)
        else:  # "Событийный принцип" - второй элемент (индекс 1)
            self.ui.t_spb.setEnabled(False)

    def choose_generator_ditribution(self):
        choose_window = ChooseDistribution(self)
        result = choose_window.exec_()  # Модальное выполнение

        if result == QDialog.Accepted and choose_window.generator is not None:
            self.generator_generator = choose_window.get_generator()
            self.ui.generator_data.setText(self.generator_generator.info())

    def choose_processor_distribution(self):
        choose_window = ChooseDistribution(self)
        result = choose_window.exec_()  
        
        if result == QDialog.Accepted and choose_window.generator is not None:
            self.processor_generator = choose_window.get_generator()
            self.ui.processor_data.setText(self.processor_generator.info())
 
    


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
