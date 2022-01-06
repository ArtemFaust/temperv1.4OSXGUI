#!/usr/bin/env ipython

from PyQt5 import QtGui, QtWidgets, QtCore, uic
import sys, time, os
import qdarkstyle, hid
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.style as style
import smtplib

style.use("dark_background")
sp = []
Manufacturer = None
Product = None
Serial = None
sp_sr = []
sendmail_status = False
cwd = os.getcwd()
print(cwd)
os.chdir(cwd)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi("./ui/main.ui", self)
        self.lineEdit_5.setValidator(QtGui.QIntValidator(-25, 55))
        self.lineEdit_4.setValidator(QtGui.QIntValidator(-25, 55))
        self.thread = ThreadToReadTemper()  # Создаем экземпляр класса потока
        self.thread.start()  # Запускаем поток
        self.thread.emiter.connect(
            self.EmiterPrint
        )  # Подключаем сигнал из потока к локальной функции
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        self.label.setPixmap(QtGui.QPixmap("Icons/TEMPer-01.png").scaled(250, 175))

        self.timer_1 = QtCore.QTimer()
        self.timer_1.setInterval(1000)
        self.timer_1.start()
        self.timer_1.timeout.connect(lambda: self.plot())

        self.timer_2 = QtCore.QTimer()
        self.timer_2.setInterval(3600000)
        self.timer_2.start()
        self.timer_2.timeout.connect(lambda: self.plot_2())
        # Виджеты графиков
        self.figure_graph1 = plt.figure()
        self.figure_graph1.patch.set_alpha(0.0)
        self.figure_graph1_canvas = FigureCanvas(self.figure_graph1)
        self.figure_graph1_ax = self.figure_graph1.add_subplot(111)
        self.figure_graph1_ax.grid(linestyle="-.", color="grey")
        self.figure_graph1_ax.set_title("Минутная статистика")
        self.verticalLayout_2.addWidget(self.figure_graph1_canvas)

        self.figure_graph2 = plt.figure()
        self.figure_graph2.patch.set_alpha(0.0)
        self.figure_graph2_canvas = FigureCanvas(self.figure_graph2)
        self.figure_graph2_ax = self.figure_graph2.add_subplot(111)
        self.figure_graph2_ax.grid(linestyle="-.", color="grey")
        self.figure_graph2_ax.set_title("Часовая статистика")
        self.verticalLayout_2.addWidget(self.figure_graph2_canvas)

        #  Вызов виджета настроек
        self.configwidget = Config_Widget()
        self.configwidget.setParent(self, QtCore.Qt.Sheet)
        self.pushButton.clicked.connect(lambda: self.configwidget.show())

    # Часовой график
    def plot_2(self):
        global sp_sr
        print("On time")
        self.figure_graph2_ax.cla()
        self.figure_graph2_ax.grid(linestyle="-.", color="grey")
        self.figure_graph2_ax.axis((0, 24, -25, 55))
        self.figure_graph2_ax.set_title("Часовая статистика")
        sr = 0
        local_sp = sp[-3600:]
        for i in local_sp:
            sr += i
        sp_sr.append(sr / len(local_sp))
        self.figure_graph2_ax.fill_between(range(0, len(sp_sr), 1), sp_sr)
        self.figure_graph2_canvas.draw()
        if len(sp_sr) == 24:
            sp_sr = []
        print("Hours graph: " + str(len(sp)) + " " + str(len(sp_sr)))

    # Минутный график
    def plot(self):
        self.figure_graph1_ax.cla()
        self.figure_graph1_ax.grid(linestyle="-.", color="grey")
        self.figure_graph1_ax.axis((0, 60, -25, 55))
        if len(sp) >= 60:
            self.figure_graph1_ax.plot(sp[-60:], color="green", label="Current")
            try:
                self.figure_graph1_ax.plot(
                    [int(self.lineEdit_4.text()) for x in range(0, 60, 1)],
                    color="red",
                    label="Critical",
                )
            except:
                pass
        else:
            self.figure_graph1_ax.plot(sp, color="green", label="Current")
            try:
                self.figure_graph1_ax.plot(
                    [int(self.lineEdit_4.text()) for x in range(0, len(sp), 1)],
                    color="red",
                    label="Critical",
                )
            except:
                pass
        self.figure_graph1_ax.set_title("Минутная статистика")
        self.figure_graph1_canvas.draw()

        self.label_5.setStyleSheet("color: green")
        self.label_5.setText(Manufacturer)
        self.label_7.setStyleSheet("color: green")
        self.label_7.setText(Product)
        self.label_9.setStyleSheet("color: green")
        self.label_9.setText(Serial)

    # Функция вызывается при поступлении сигнала из потока
    def EmiterPrint(self, emit_text):
        global sp, sendmail_status
        if emit_text != "Non connection!" and emit_text != "Connection lost!":
            try:
                sp.append(float(emit_text) + float(self.lineEdit_5.text()))
                # реализовать отправку на эмаил
                if int(float(emit_text) + float(self.lineEdit_5.text())) > int(
                    self.lineEdit_4.text()
                ):
                    if self.checkBox.isChecked():
                        if os.path.exists("conf.ini") and not sendmail_status:
                            file = open("conf.ini", "r")
                            line = file.read()
                            lines = line.split("\n")
                            sendler = lines[0]
                            sendler = sendler.split("Sendler=")
                            sendler = sendler[1]
                            sendler_user = sendler.split(":")[0]
                            sendler_password = sendler.split(":")[1]
                            sent_from = sendler_user.split("@")[0]
                            print(sendler_user)
                            print(sendler_password)

                            Recipients = lines[1]
                            Recipients = Recipients.split("Recipients=")
                            Recipients = Recipients[1]
                            Recipients = Recipients.split(",")
                            print(Recipients)
                            # Send email
                            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                            server.ehlo()

                            try:
                                server.login(sendler_user, sendler_password)
                                to = Recipients
                                subject = "Temperv!.4"
                                body = "Temperature allert! = " + str(
                                    int(
                                        float(emit_text) + float(self.lineEdit_5.text())
                                    )
                                )

                                server.sendmail(sent_from, to, body)
                                server.close()
                                print("Сообщение отправленно!")
                                sendmail_status = True
                            except Exception as e:
                                print(e)
                else:
                    sendmail_status = False
                if int(float(emit_text) + float(self.lineEdit_5.text())) < int(
                    self.lineEdit_4.text()
                ):
                    self.label_13.setStyleSheet("color: green")
                else:
                    self.label_13.setStyleSheet("color: red")
                self.label_13.setText(
                    str(float(emit_text) + float(self.lineEdit_5.text())) + " C˚"
                )
                if int(float(max(sp)) + float(self.lineEdit_5.text())) > int(
                    self.lineEdit_4.text()
                ):
                    self.label_16.setStyleSheet("color: red")
                else:
                    self.label_16.setStyleSheet("color: green")
                self.label_16.setText(str(max(sp)) + " C˚")
                if int(float(min(sp)) + float(self.lineEdit_5.text())) > int(
                    self.lineEdit_4.text()
                ):
                    self.label_17.setStyleSheet("color: red")
                else:
                    self.label_17.setStyleSheet("color: green")
                self.label_17.setText(str(min(sp)) + " C˚")
            except ValueError:
                pass

        elif emit_text == "Connection lost!":
            self.label_13.setStyleSheet("color: red")
            self.label_13.setText("Connection lost!")
            self.label_5.setStyleSheet("color: red")
            self.label_5.setText("Connection lost!")
            self.label_7.setStyleSheet("color: red")
            self.label_7.setText("Connection lost!")
            self.label_9.setStyleSheet("color: red")
            self.label_9.setText("Connection lost!")

        else:
            self.label_13.setStyleSheet("color: red")
            self.label_13.setText("Non connection!")
            self.label_5.setStyleSheet("color: red")
            self.label_5.setText("Non connection!")
            self.label_7.setStyleSheet("color: red")
            self.label_7.setText("Non connection!")
            self.label_9.setStyleSheet("color: red")
            self.label_9.setText("Non connection!")


# Клас потока
class ThreadToReadTemper(QtCore.QThread):
    def __init__(self):  # инициализация класа
        QtCore.QThread.__init__(self)  # инициализация потока

    emiter = QtCore.pyqtSignal(
        str
    )  # эмитер (сигнал) который передает переменную тима строки

    def run(self):  # Собственно функция потока
        global Manufacturer, Product, Serial
        h = hid.device(0x0C45, 0x7401)
        open = False
        i = 0
        while not open:
            try:
                h.open(0x0C45, 0x7401)
                open = True
                i = 0
            except:
                i += 1
                if i > 20:
                    self.emiter.emit("Non connection!")
        h.write([0x01, 0x82, 0x77, 0x01, 0x00, 0x00, 0x00, 0x00])
        h.write([0x01, 0x86, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00])
        Manufacturer = h.get_manufacturer_string()
        Product = h.get_product_string()
        try:
            Serial = h.get_serial_number_string()
        except:
            Serial = "Error get serial number!"
        h.close()
        open = False
        i = 0
        while True:
            while not open:
                try:
                    h.open(0x0C45, 0x7401)
                    open = True
                    i = 0
                except:
                    i += 1
                    if i > 20:
                        self.emiter.emit("Connection lost!")
            h.set_nonblocking(1)
            h.write([0x01, 0x80, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00])
            try:
                data = h.read(64)
            except:
                self.emiter.emit("Connection lost!")
                open = False
                break
            try:
                temp = (data[3] & 0xFF) + (data[2] << 8)
                temp_c = temp * (125.0 / 32000.0)
                if int(temp_c) == 77 or int(temp_c) == 208:
                    pass
                else:
                    self.emiter.emit(
                        str(float("%.3f" % temp_c))
                    )  # вызывает функцию emit у эмитера для передачи сигнала в основной поток
                time.sleep(1)
                h.close()
                open = False
            except:
                pass


# Виджет настроек
class Config_Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.ui = uic.loadUi("ui/conf.ui", self)
        self.pushButton_2.clicked.connect(lambda: self.hide())
        self.pushButton.clicked.connect(self.save_conf)

    def save_conf(self):
        if self.lineEdit.text() and self.lineEdit_3.text():
            if "@gmail.com" in self.lineEdit.text():
                if self.textEdit.toPlainText() != "":
                    line = self.textEdit.toPlainText()
                    file = open("conf.ini", "w")
                    file.write(
                        "Sendler=%s" % self.lineEdit.text()
                        + ":%s" % self.lineEdit_3.text()
                        + "\n"
                        + "Recipients=%s" % line
                    )
                    file.close()
                    QtWidgets.QMessageBox.information(self, "Уведомление", "Сохранил!")
                else:
                    QtWidgets.QMessageBox.information(
                        self, "Уведомление", "Не указанны получатели!"
                    )
            else:
                QtWidgets.QMessageBox.information(
                    self,
                    "Уведомление",
                    "Можно использовать только\nпочтовые ячики gmail!",
                )


app = QtWidgets.QApplication(sys.argv)
Form = MainWindow()
Form.show()
sys.exit(app.exec_())
