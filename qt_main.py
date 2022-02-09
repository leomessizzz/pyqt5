import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from PyQt5.QtCore import QTimer
from mygui import Ui_MainWindow

serial_opend_by_self = False            #串口是否是本程序打开的
class Pyqt5_Serial(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Pyqt5_Serial, self).__init__()
        self.setupUi(self)
        self.init()
        self.setWindowTitle("qt串口助手")
        self.ser = serial.Serial()
        self.port_check()

        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.s4_line_1.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.s4_line_2.setText(str(self.data_num_sended))

    def init(self):
        # # 串口检测按钮
        # self.s1_but_1.clicked.connect(self.port_check)

        # 串口信息显示
        self.s1_box_1.currentTextChanged.connect(self.port_imf)

        # 打开和关闭串口按钮
        self.s1_but_2.clicked.connect(self.port_status_check)


        # 发送数据按钮
        self.s6_but_1.clicked.connect(self.data_send)

        # 定时发送数据
        self.timer_send = QTimer()
        self.timer_send.timeout.connect(self.data_send)
        self.s3_ckbox_2.stateChanged.connect(self.data_send_timer)

        # 定时端口扫描
        self.timer_port_scan = QTimer()
        self.timer_port_scan.timeout.connect(self.port_check)
        self.timer_port_scan.start(1000)  # 每隔1000ms扫描一次端口

        # 定时器接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)

        # # 清除发送窗口
        # self.s2_but_1.clicked.connect(self.send_data_clear)

        # 清除接收窗口
        self.s2_but_1.clicked.connect(self.receive_data_clear)

    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1_box_1.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1_box_1.addItem(port[0])
        # print ("port check\n")
        if len(self.Com_Dict) == 0:
            pass
            self.s1_lab_state.setText(" 无串口")

    def port_status_check(self):
        global serial_opend_by_self
        if self.ser.isOpen() and serial_opend_by_self == True:
            self.port_close()
        else:
            self.port_open()

    # 串口信息
    def port_imf(self):
        # 显示选定的串口的详细信息
        imf_s = self.s1_box_1.currentText()
        if imf_s != "":
            self.s1_lab_state.setText(self.Com_Dict[self.s1_box_1.currentText()])

    # 打开串口
    def port_open(self):
        global serial_opend_by_self
        try:
            self.ser.port = self.s1_box_1.currentText()
            self.ser.baudrate = int(self.s1_box_2.currentText())
            self.ser.bytesize = int(self.s1_box_3.currentText())
            self.ser.stopbits = int(self.s1_box_5.currentText())
            self.ser.parity = self.s1_box_4.currentText()
        except:
            print("串口配置失败\n")
            return
        try:
            self.ser.open()
        except:
            print("串口打开失败！")
            QMessageBox.critical(self, "Port Error", "串口打开失败，请检查串口是否存在或是否被占用！")
            return None

        # 打开串口接收定时器，周期为2ms
        self.timer.start(2)

        if self.ser.isOpen():
            self.s1_but_2.setText("关闭串口（已开启）")
            self.s4.setTitle("串口状态（已开启）")
            self.timer_port_scan.stop()                 # 端口定时扫描关闭
            self.s6_but_1.setEnabled(True)              # 数据发送按钮使能
            self.s3_ckbox_2.setEnabled(True)            # 定时发送选择使能
            self.s1_box_1.setEnabled(False)              # 端口号选择失能
            self.s1_box_2.setEnabled(False)              # 波特率选择失能
            self.s1_box_3.setEnabled(False)              # 数据位选择失能
            self.s1_box_4.setEnabled(False)              # 校验位选择失能
            self.s1_box_5.setEnabled(False)              # 停止位选择失能
            serial_opend_by_self = True                 # 本程序打开串口标志为真

    # 关闭串口
    def port_close(self):
        global serial_opend_by_self
        self.timer.stop()
        self.timer_send.stop()
        try:
            self.ser.close()
        except:
            pass
        self.s1_but_2.setText("打开串口（已关闭）")

        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.s4_line_1.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.s4_line_2.setText(str(self.data_num_sended))
        self.s4.setTitle("串口状态（已关闭）")
        self.timer_port_scan.start(1000)                # 每隔1000ms扫描一次端口
        self.s3_line_1.setEnabled(True)
        self.s6_but_1.setEnabled(False)                 # 数据发送按钮失能
        self.s3_ckbox_2.setEnabled(False)               # 定时发送选择失能
        self.s1_box_1.setEnabled(True)                  # 端口号选择使能
        self.s1_box_2.setEnabled(True)                  # 波特率选择使能
        self.s1_box_3.setEnabled(True)                  # 数据位选择使能
        self.s1_box_4.setEnabled(True)                  # 校验位选择使能
        self.s1_box_5.setEnabled(True)                  # 停止位选择使能
        serial_opend_by_self = False                    # 本程序打开串口标志为假


    # 发送数据
    def data_send(self):
        if self.ser.isOpen():
            input_s = self.s6_text_1.toPlainText()
            if input_s != "":
                # 非空字符串
                if self.s3_ckbox_1.isChecked():
                    # hex发送
                    input_s = input_s.strip()
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)
                        except ValueError:
                            QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                            return None
                        input_s = input_s[2:].strip()
                        send_list.append(num)
                    input_s = bytes(send_list)
                else:
                    # ascii发送
                    input_s = (input_s + '\r\n').encode('utf-8')

                num = self.ser.write(input_s)
                self.data_num_sended += num
                self.s4_line_2.setText(str(self.data_num_sended))
            else:
                self.s5_text_1.insertPlainText("发送数据为空，发送失败！\n")

        else:
            print("发送失败")
            QMessageBox.critical(self, "Port Error", "数据发送失败，请检查串口是否打开！")
            pass

    # 接收数据
    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0:
            data = self.ser.read(num)
            num = len(data)
            # hex显示
            if self.s2_ckbox_1.checkState():
                out_s = ''
                for i in range(0, len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '
                self.s5_text_1.insertPlainText(out_s)
            else:
                # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
                self.s5_text_1.insertPlainText(data.decode('utf-8'))

            # 统计接收字符的数量
            self.data_num_received += num
            self.s4_line_1.setText(str(self.data_num_received))

            # 获取到text光标
            textCursor = self.s5_text_1.textCursor()
            # 滚动到底部
            textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
            self.s5_text_1.setTextCursor(textCursor)
        else:
            pass

    # 定时发送数据
    def data_send_timer(self):
        if self.s3_ckbox_2.isChecked():
            self.timer_send.start(int(self.s3_line_1.text()))
            self.s3_line_1.setEnabled(False)
        else:
            self.timer_send.stop()
            self.s3_line_1.setEnabled(True)

    # 清除显示
    def send_data_clear(self):
        self.s6_text_1.setText("")

    def receive_data_clear(self):
        self.s5_text_1.setText("")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    myshow.show()
    sys.exit(app.exec_())
