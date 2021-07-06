# -*- coding: utf-8 -*-

import sys
from user_changeNameUI import Ui_Dialog_ChangeFileName
from threading       import Thread
from user_loginUI    import Ui_Dialog_Login
from user_receive    import *
from user_database   import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIntValidator
from progressUI      import Ui_Dialog_Progress
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QLineEdit,QApplication, QDialog
from user_mainUI import Ui_MainWindow
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QStringListModel
from setUI             import   Ui_Dialog_Set

class MyProgress(QDialog, Ui_Dialog_Progress):
    progressBarValue = pyqtSignal(str, int, int)
    def __init__(self):
        super(MyProgress, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
    def do_myprocress_show(self, s, num_newfile, num_receive):
        self.progressBar.setRange(0, num_newfile)
        self.label_Progress.setText("正在{}文件.......".format(s))
        self.progressBar.setValue(num_receive)

class MySet(QDialog, Ui_Dialog_Set):
    def __init__(self):
        super(MySet, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

    def show(self):
        self.setVisible(True)
        with open('userInfoSet.json', 'r',encoding='UTF-8') as f1:
            data = json.load(f1)
            info = str(data)
            self.textEdit_set.setText(info)

    def accept(self):
        info = self.textEdit_set.toPlainText()
        with open('newNetInfo.json', 'w') as f1:
            json.dump(info, f1)
        self.setVisible(False)


class MyDialog(QDialog, Ui_Dialog_Login):
    def __init__(self):
        super(MyDialog, self).__init__()
        self.setupUi(self)
        self.setDialog = MySet()
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_QuitOnClose)
        self.LineEdit_Password.setEchoMode(QLineEdit.Password)
        self.pushButton_Login.clicked.connect(self.login)
        self.pushButton_Set.clicked.connect(self.set)
        self.closesw = True
        with open('newNetInfo.json', 'r') as f1:
            self.data = json.load(f1)
            f1.close()
        self.LineEdit_ServerIP.setText(self.data["MainServerTrueAdd"][0])
        self.LineEdit_ServerPort.setText(str(self.data["MainServerTrueAdd"][1]))
        self.LineEdit_Password.setText(self.data["user_password"])

    def set(self):
        self.setDialog.show()

    def login(self):
        #self.lineEdit_Tip_login.setVisible(True)
        # 将login界面输入的服务器地址和端口号保存在netInfo.json中
        server_ip = self.LineEdit_ServerIP.text()
        server_port = int(self.LineEdit_ServerPort.text())
        # self.data是读取netInfo.json的数据
        self.data["MainServerTrueAdd"][0] = server_ip
        self.data["MainServerTrueAdd"][1] = server_port
        with open('userInfoSet.json', 'r', encoding='UTF-8') as f:
            dd = json.load(f)
            f.close()
        username = self.comboBox_Name.currentText()
        self.data["user_name"] = dd["client"][username][0]
        self.data["user_password"] = self.LineEdit_Password.text().strip(" ")
        # 如果本机有多个IP地址，则要根据服务器IP地址，将客户端程序的IP地址设置在与服务器同一个网址段内
        ll = server_ip.split(".")
        ipstr = "{}.{}.{}".format(ll[0], ll[1], ll[2]) # 提取服务器ip地址前3段
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip.startswith(ipstr):
                self.data["user_ip"] = ip
                break
        with open('newNetInfo.json', 'w') as f2:
            json.dump(self.data, f2)
            f2.close()
        if self.data["user_password"] == "":
            QMessageBox.critical(self, "错误", "请输入密码！")
        else:
            # 发送指令'$Login$'，请求登录
            server_Address = tuple(self.data["MainServerTrueAdd"])
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.connect(server_Address)
            except Exception as e:
                QMessageBox.critical(self, "错误", "服务器未启动,请稍后再试！")
            else:
                with open('newNetInfo.json', 'r') as f:
                    data = json.load(f)
                    f.close()
                data["CMD"] = '$Login$'
                header_json = json.dumps(data)
                header_bytes = header_json.encode('utf-8')
                sock.send(struct.pack('i', len(header_bytes)))
                sock.send(header_bytes)
                # 1接受报头长度
                obj = sock.recv(4)
                header_size = struct.unpack('i', obj)[0]
                # 2接收报头
                header_bytes = sock.recv(header_size)
                header_json = header_bytes.decode('utf-8')
                header_dic = json.loads(header_json)
                # 收到指令'$Allowed$'，登录
                # 在这里要记录服务器为用户开辟的新端口
                if "$Allowed$" in header_dic['CMD'] :
                    cmdlist = header_dic['CMD'].split("$")
                    # 保存与服务器会话地址
                    with open('newNetInfo.json', 'w') as f2:
                        self.data["MainServerTempAdd"][0] = cmdlist[2]
                        self.data["MainServerTempAdd"][1] = int(cmdlist[3])
                        json.dump(self.data,f2)
                        f2.close()
                    self.closesw = False
                    self.close()#此处登录对话框已经关闭，是否意味主动套接字结束
                    time.sleep(0.2)
                    win.show()
                    win.do_inital()
                elif header_dic['CMD'] == "$Denied$":
                    QMessageBox.critical(self, "错误", "密码输入错误！")
        # 保存密码为否时，清空密码
        if not self.checkBox.isChecked():
            self.data["user_password"] = ""
        with open('newNetInfo.json', 'w') as f2:
            json.dump(self.data, f2)
            f2.close()
        self.pushButton_Login.setEnabled(True)
    def closeEvent(self, event):
        if self.closesw:
            os._exit(0)
class ChangeNameDialog(QDialog,Ui_Dialog_ChangeFileName):
    def __init__(self):
        super(ChangeNameDialog, self).__init__()
        self.setupUi(self)
        self.LineEdit_Dlg_Pnum.setValidator(QIntValidator(0, 60))
        self.LineEdit_Dlg_Unum.setValidator(QIntValidator(0, 60))
        self.comboBox_Dlg_What.currentTextChanged.connect(self.comboBox_Dlg_What_changed)
        self.pushButton_SelAll.clicked.connect(self.selAll)
        self.pushButton_SelOne.clicked.connect(self.selOne)
        self.pushButton_DelAll.clicked.connect(self.delAll)
        self.pushButton_DelOne.clicked.connect(self.delOne)
        self.pushButton_FindBank.clicked.connect(self.findBank)
        self.listView_BankList.doubleClicked.connect(self.doubleclik)
        self.listView_BankList_Sel.doubleClicked.connect(self.doubleclik_sel)
        with open('.\\banklist.json', 'r', encoding='UTF-8') as f:  # 打开文件用于读
            data = json.load(f)
            f.close()
        self.banklist = data["banklist"]
        self.banklist_model = QStringListModel()
        self.banklist_model.setStringList(self.banklist)
        self.listView_BankList.setModel(self.banklist_model)


        self.banklist_sel=[]
        self.banklist_sel_model = QStringListModel()
        self.banklist_sel_model.setStringList(self.banklist_sel)
        self.listView_BankList_Sel.setModel(self.banklist_sel_model)
    def doubleclik(self):
        self.selOne()
    def doubleclik_sel(self):
        self.delOne()

    def selAll(self):
        with open('.\\banklist.json', 'r', encoding='UTF-8') as f:  # 打开文件用于读
            data = json.load(f)
            f.close()
        self.banklist = data["banklist"]
        self.banklist_sel = self.banklist
        self.banklist_sel_model.setStringList(self.banklist_sel)


    def selOne(self):
        sw = True
        item = self.listView_BankList.currentIndex().row()# item为当前选中行行号，默认未选中时，item =-1，是最后一项
        if item >= 0:
            #print("item {}".format(item))
            value = self.banklist_model.stringList()[item]
            if self.banklist_sel == []:
                self.banklist_sel.append(value)
            else:
                for i in range(len(self.banklist_sel)):
                    if value == self.banklist_sel[i]:
                        sw = False
                        break
                if sw:
                    self.banklist_sel.append(value)
            self.banklist_sel_model.setStringList(self.banklist_sel)

    def delAll(self):
        self.banklist_sel = []
        self.banklist_sel_model.setStringList(self.banklist_sel)

    def delOne(self):
        #print(self.banklist_sel)
        item = self.listView_BankList_Sel.currentIndex().row()
        #print("item{}".format(item))
        if item >=0:
            item = self.listView_BankList_Sel.currentIndex().row()
            value = self.banklist_sel_model.stringList()[item]
            self.banklist_sel.remove(value)
        self.banklist_sel_model.setStringList(self.banklist_sel)
    def findBank(self):
        bank = self.lineEdit_FindBank.text()
        s = False
        for row in range(self.banklist_model.rowCount()):
            index = self.banklist_model.index(row,0)
           # item = self.banklist_model.data(index)
            item = self.banklist_model.data(index,  Qt.DisplayRole)
            if bank in item:
                self.listView_BankList.setCurrentIndex(index)
                s =True
                #print(item)
                break
        if not s:
            QMessageBox.critical(self, "提示", "你要添加的银行不存在！")


    def comboBox_Dlg_What_changed(self):
        text = self.comboBox_Dlg_What.currentText()
        if  text == "银行流水":
            self.resize(800, 880)
            self.setMinimumSize(QtCore.QSize(800, 880))
            self.setMaximumSize(QtCore.QSize(800, 880))
        else:

            self.resize(800, 220)
            self.setMinimumSize(QtCore.QSize(800, 220))
            self.setMaximumSize(QtCore.QSize(800, 220))
    def setDatas(self, value):
        self.LineEdit_Dlg_Filename.setText(value)



    def returnDatas(self):
        dlgFilename = self.LineEdit_Dlg_Filename.text()
        dlgWhat     = self.comboBox_Dlg_What.currentText()
        dlgUser     = self.comboBox_Dlg_User.currentText()
        dlgWho      = self.LineEdit_Dlg_Who.text()
        dlgPnum     = self.LineEdit_Dlg_Pnum.text()
        dlgUnum     = self.LineEdit_Dlg_Unum.text()
        dlgSms      = self.textEdit_Dlg_Sms.toPlainText()
        text = self.comboBox_Dlg_What.currentText()
        if text == "银行流水":
            dlgBankCode = self.banklist_sel
            if dlgBankCode == []:
                QMessageBox.critical(self, "错误", "请选择需要查询的银行！")
                dlgInfo = []
                return dlgInfo
        else:
            dlgBankCode = []
        dlgBankCodeBack = []
        dlgInfo     = [dlgFilename, dlgWhat, dlgUser, dlgWho, dlgPnum, dlgUnum, dlgBankCode, dlgBankCodeBack, dlgSms]
        # 只要dlgInfo中除短消息外，有一项信息不全，就设置为空
        for i in range(len(dlgInfo)-1):
            if dlgInfo[i] == "":
                dlgInfo = []
                break


        return dlgInfo

    
class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        self.showsw =True
        self.isfirst = True
        self.num_send = 0
        self.num_newfile = 0
        self.num_left = 0
        self.fileName_full = ""
        self.fileName_base = ""
        self.fileType = ""
        # 保存curidx值，是为了在查询记录中，使用next和forward功能继续搜索未搜索的记录，不需要从头开始
        self.curidx = 0
        self.forward = False
        self.backward = False
        self.tempidx = 0
        self.userdatabase = MySqlTableModel()
        super(MainForm, self).__init__()
        self.setupUi(self)

        self.setWindowFlags(
            Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.desktop = QApplication.desktop()
        # 获取显示器分辨率大小
        self.screenRect = self.desktop.screenGeometry()
        height = self.screenRect.height()
        width = self.screenRect.width()
        self.setMaximumSize(QtCore.QSize(width, height))

        # 设置选中时是整行选中
        self.tableView_Data.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_Data.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView_Data.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView_Data.setAlternatingRowColors(True)
        self.pushButton_OpenFile.clicked.connect(self.do_OpenFile)
        self.pushButton_OpenFeedback.clicked.connect(self.do_OpenFeedback)
        self.pushButton_ReceiveFile.clicked.connect(self.do_receiveFile)
        self.pushButton_SendFile.clicked.connect(self.do_sendFile)
        self.pushButton_Concel.clicked.connect(self.do_concel)
        self.pushButton_Delete.clicked.connect(self.do_delete)
        self.pushButton_Search.clicked.connect(self.do_search)
     #   self.tableView_Data.clicked.connect(self.do_clicked)
        self.tableView_Data.doubleClicked.connect(self.do_doubleclicked)
        self.userdatabase.user_Database_init(self)
        self.userdatabase.selModel.currentRowChanged.connect(self.do_currentRowChanged)

        self.pushButton_Find.clicked.connect(self.do_find)
        self.pushButton_Forward.clicked.connect(self.do_forward)
        self.pushButton_Backward.clicked.connect(self.do_backward)
        self.comboBox_area.currentIndexChanged.connect(self.do_combochange)
        self.lineEdit_keyword.textChanged.connect(self.do_keywordchange)

        path = os.getcwd()
        filelist = os.listdir("{}{}".format(path, "\\TempFolderSend\\"))
        if filelist:
            self.pushButton_SendFile.setEnabled(True)
        else:
            self.pushButton_SendFile.setEnabled(False)
        self.progress = MyProgress()



    def do_inital(self):
        # 提示有几个查询需要发送
        self.num_send = int(len(os.listdir(".\\TempFolderSend\\"))/2)
        self.do_showtip(self.pushButton_SendFile, self.lineEdit_Tip_send, self.num_send)
        if self.num_send:
            self.pushButton_SendFile.setEnabled(True)
        else:
            self.pushButton_SendFile.setEnabled(False)

    def do_showtip(self, btn, edit, num):
        if num:
            x = btn.x()
            y = btn.y()
            if int(num) < 100:
                edit.setGeometry(x + 60, y - 10, 20, 20)
            else:
                edit.setGeometry(x + 60, y - 10, 30, 20)
            ch = str(num)
            edit.setText(ch)
            edit.setVisible(True)
        else:
            edit.setVisible(False)

    def do_combochange(self):
        # combobox中查询范围发生变化时，将curidx复位
        self.curidx = 0
        self.forward = False
        self.backward = False
        self.tableView_Data.clearSelection()
        self.pushButton_OpenFeedback.setEnabled(False)
        self.pushButton_Concel.setEnabled(False)
        self.pushButton_Delete.setEnabled(False)

    def do_keywordchange(self):
        # keyword中查询范围发生变化时，将curidx复位
        self.curidx = 0
        self.forward = False
        self.backward = False
        self.tableView_Data.clearSelection()
        self.pushButton_OpenFeedback.setEnabled(False)
        self.pushButton_Concel.setEnabled(False)
        self.pushButton_Delete.setEnabled(False)

    def do_find(self):
        self.curidx = 0
        area = self.comboBox_area.currentText()
        keyword = self.lineEdit_keyword.text()
        keyword = keyword.strip(" ")
        if keyword == "":
            QMessageBox.warning(self, "提示", "请输入关键字！")
            return
        thereis = False
      #  for self.curidx in range(self.tabModel.rowCount()):
        while self.curidx < self.userdatabase.tabModel.rowCount():
            rec = self.userdatabase.tabModel.record(self.curidx)
            if keyword in rec.value(area):
                self.tableView_Data.selectRow(self.curidx)
                thereis = True
                break
            self.curidx = self.curidx + 1
        if not thereis:
            QMessageBox.warning(self, "提示", "没有发现记录！")
            # 取消选中行的高亮状态
            self.tableView_Data.clearSelection()
            self.forward = False
            self.backward = False
        else:
            self.forward = True
            self.backward = True
    def do_backward(self):
        if self.forward:
            area = self.comboBox_area.currentText()
            keyword = self.lineEdit_keyword.text()
            thereis = False
            while self.curidx >= 0:
                if self.curidx >= 0:
                    self.curidx = self.curidx - 1
                    rec = self.userdatabase.tabModel.record(self.curidx)
                    if keyword in rec.value(area):
                        self.tableView_Data.selectRow(self.curidx)
                        thereis = True
                        self.tempidx = self.curidx
                        break
                else:
                    self.curidx = self.curidx + 1
                    break
            if not thereis:
                self.curidx = self.tempidx
                QMessageBox.warning(self, "提示", "查询完毕！")

    def do_forward(self):
        if self.forward:
            area = self.comboBox_area.currentText()
            keyword = self.lineEdit_keyword.text()
            thereis = False
            while self.curidx < self.userdatabase.tabModel.rowCount():
                self.curidx = self.curidx + 1
                if self.curidx < self.userdatabase.tabModel.rowCount():
                    rec = self.userdatabase.tabModel.record(self.curidx)
                    if keyword in rec.value(area):
                        self.tableView_Data.selectRow(self.curidx)
                        thereis = True
                        self.tempidx = self.curidx
                        break
                else:
                    self.curidx = self.curidx - 1
                    break
            if not thereis:
                self.curidx =self.tempidx
                QMessageBox.warning(self, "提示", "查询完毕！")

    def do_search(self):
        self.pushButton_OpenFeedback.setEnabled(False)
        self.pushButton_Concel.setEnabled(False)
        self.pushButton_Delete.setEnabled(False)
        rec = self.textBrowser_Info.geometry()
        x = rec.left()
        y = rec.height() + rec.top()
        self.Frame.setGeometry(x+1, y - 39, rec.width()-3, 36)
        if self.Frame.isHidden():
            self.Frame.show()
        else:
            self.Frame.hide()



    def resizeEvent(self, event):
        # 当窗体初始化后第一次显示时，会产生resizeEvent事件，会错误显示self.frame
        if self.isfirst:
            self.isfirst =False
        else:
            rec = self.textBrowser_Info.geometry()
            x = rec.left()
            y = rec.height() + rec.top()
            self.Frame.setGeometry(x + 1, y - 39, rec.width() - 3, 36)
            if not self.Frame.isHidden():
                self.Frame.show()

    def do_delete(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        curRecNo = self.userdatabase.selModel.currentIndex().row()
        curRec = self.userdatabase.tabModel.record(curRecNo)
        filename = curRec.value("查询文件编号")
        if filename == "":
            QMessageBox.warning(self, '错误', '请选择需要删除的记录！')
            return
        path = os.getcwd()
        orignalFeFileName_base = os.path.basename(curRec.value("查询文件名称"))
        f, ftype = os.path.splitext(orignalFeFileName_base)
        if curRec.value("发送状态") == "未发送":
            reply = QMessageBox.warning(self, '警告', '你确定需要删除当前记录?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.userdatabase.tabModel.removeRow(curRecNo)
                self.userdatabase.tabModel.submitAll()
                self.userdatabase.tabModel.setSort(13, Qt.AscendingOrder)
                self.userdatabase.tabModel.select()

                file = os.listdir("{}{}".format(path, "\\TempFolderSend\\"))
                for f in file:
                    if filename in f:
                        os.remove( "{}{}{}".format(path, "\\TempFolderSend\\", f))

                file = os.listdir("{}{}".format(path, "\\FolderSend\\"))
                for f in file:
                    if filename in f:
                        os.remove("{}{}{}".format(path, "\\FolderSend\\", f))

                self.pushButton_Delete.setEnabled(False)
                self.num_send = self.num_send - 1
                self.do_showtip(self.pushButton_SendFile, self.lineEdit_Tip_send, self.num_send)
            else:
                self.pushButton_Delete.setEnabled(False)
            path = os.getcwd()
            filelist = os.listdir("{}{}".format(path, "\\TempFolderSend\\"))
            if filelist:
                self.pushButton_SendFile.setEnabled(True)
            else:
                self.pushButton_SendFile.setEnabled(False)
        else:
            QMessageBox.critical(self, "错误", "当前记录不可删除！")

    #  撤销查询
    def do_concel(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        curRecNo = self.userdatabase.selModel.currentIndex().row()
        curRec = self.userdatabase.tabModel.record(curRecNo)
        if curRec.value("查询文件编号") == "":
            QMessageBox.warning(self, "错误", "请选择需要撤销的查询！")
            return

        if (curRec.value("查询时间") != "") and (curRec.value("反馈时间") == ""):
            concelFileName = curRec.value("查询文件编号")
            cmd = "${}${}$".format("Concel", concelFileName)
            with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
                data = json.load(f)
            try:
                user_send(self, tuple(data["MainServerTempAdd"]), cmd,[])
            except Exception as e:
                self.do_message("当前查询无法撤销，原因：{}。".format(e), "#FFFFFF")
            else:
                self.do_message("已通知服务器撤销编号为{}的查询！".format(concelFileName), "#FFFFFF")

        self.userdatabase.tabModel.setSort(13, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()
    def do_OpenFeedback(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        path = os.getcwd()
        curRecNo = self.userdatabase.selModel.currentIndex().row()
        curRec = self.userdatabase.tabModel.record(curRecNo)

        if curRec.value("反馈状态") == "未反馈":
            QMessageBox.warning(self, "提示", "当前查询没有反馈！")
            return
        filename = curRec.value("反馈文件名称")
        status = curRec.value("反馈状态")
        if filename != "":
            filepath = "{}{}".format(path, "\\FolderReceive\\")
            os.startfile(filepath)
            if status == "部分反馈":
                self.userdatabase.tabModel.setData(self.userdatabase.tabModel.index(curRecNo, 13), 2)
            elif status == "全部反馈":
                self.userdatabase.tabModel.setData(self.userdatabase.tabModel.index(curRecNo, 13), 3)
                self.userdatabase.tabModel.setData(self.userdatabase.tabModel.index(curRecNo, 11), "结束归档")
        else:
            QMessageBox.warning(self, "提示", "请选择要查看的反馈记录！")
        self.pushButton_OpenFeedback.setEnabled(False)
        self.userdatabase.tabModel.setSort(13, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()

    def do_OpenFile(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        self.pushButton_Concel.setEnabled(False)
        self.pushButton_OpenFeedback.setEnabled(False)
        self.pushButton_Delete.setEnabled(False)
        self.pushButton_ReceiveFile.setEnabled(False)
        self.pushButton_SendFile.setEnabled(False)
        self.fileName_full, self.fileType = QtWidgets.QFileDialog.getOpenFileName(self, "Select file", os.getcwd(),
                                                                   "All Files(*)")
        if self.fileName_full == "":
            QMessageBox.critical(self, "错误", "请选择要发送的查询文书！")
        else:
            changeDlg = ChangeNameDialog() ##!!!更名入库函数
            changeDlg.setDatas(self.fileName_full)  # 将查询文书的原始名称传入更名入库对话框中
            i = changeDlg.exec_()
            if i:
                # 获取查询信息对话框反馈的内容
                dlgInfo = changeDlg.returnDatas()
               # print(dlgInfo)
                if dlgInfo != []:
                        # 将查询信息对话框反馈的内容添加入数据库
                     #   print(dlgInfo)
                        self.userdatabase.do_addRecord(dlgInfo)
                        self.pushButton_SendFile.setEnabled(True)
                        self.num_send = self.num_send + 1
                        self.do_showtip(self.pushButton_SendFile, self.lineEdit_Tip_send, self.num_send)
                else:
                    QMessageBox.critical(self, "错误", "信息填写不完整！")

            else:
                QMessageBox.critical(self, "错误", "请选择要发送的查询文书！")
        self.userdatabase.tabModel.setSort(13, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()


    def do_sendFile(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        self.pushButton_OpenFeedback.setEnabled(False)
        with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
            data = json.load(f)
        server_Address = tuple(data["MainServerTempAdd"])
        path = os.getcwd()
        filelist = os.listdir("{}{}".format(path, "\\TempFolderSend\\"))
        self.num_newfile = len(filelist)
        self.num_left = 1
        if filelist == []:
            QMessageBox.warning(self, "提示", "当前没有需要发送的查询！")
        else:
            self.do_message("正在等待服务器响应！", "#FFFFFF")
            #print("filelist:{}".format(filelist))
            try:
                user_send(self, server_Address, "$JW$IsReadyToSendFile$", filelist)
           # i = user_send_CMD(server_Address, "$JW$IsReadyToSendFile$") #------------->send CMD
            ###等待服务器回应cmd---ready
            ###进入cmd处理程序，一个接一个发送文件，而不是一起发送，每发送完一个文件等待服务器回应ready，然后再发送下一个文件
            except Exception as e:
                #print("user send error:{}".format(e))
                self.do_message("发送文件错误：{}！".format(e), "#FFFFFF")
                self.pushButton_SendFile.setEnabled(True)
                self.pushButton_Delete.setEnabled(True)
            else:
                self.do_message("服务器已启动！", "#FFFFFF")
                progress.do_myprocress_show("发送", self.num_newfile, self.num_left)
                progress.show()
                #user_send_File(self, server_Address, filelist)            #--------------->send file
                self.pushButton_SendFile.setEnabled(False)
                self.pushButton_Delete.setEnabled(False)
                self.num_send = 0
                self.do_showtip(self.pushButton_SendFile, self.lineEdit_Tip_send, self.num_send)
        self.userdatabase.tabModel.setSort(13, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()
    def do_receiveFile(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
            data = json.load(f)
        server_Address = tuple(data["MainServerTempAdd"])
        self.do_message("正在等待服务器响应！", "#FFFFFF")
        try:
            user_send(self, server_Address, "$WeNeedFileFromOT$",[])
        except Exception as e:
            self.do_message("服务器未响应，原因：{}。".format(e), "#FFFFFF")
        else:
            self.do_message("服务器已启动！", "#FFFFFF")
            progress.show()
        self.pushButton_Concel.setEnabled(False)
        self.pushButton_OpenFeedback.setEnabled(False)
        self.pushButton_Delete.setEnabled(False)
        self.userdatabase.tabModel.setSort(13, Qt.AscendingOrder)
        self.userdatabase.tabModel.select()

    def do_currentRowChanged(self, current):
        self.userdatabase.mapper.setCurrentIndex(current.row())
        path = os.getcwd()
        filelist = os.listdir("{}{}".format(path, "\\TempFolderSend\\"))
        if filelist:
            self.pushButton_SendFile.setEnabled(True)
        else:
            self.pushButton_SendFile.setEnabled(False)
        curRecNo = self.userdatabase.selModel.currentIndex().row()
        curRec = self.userdatabase.tabModel.record(curRecNo)
        status1 = curRec.value("反馈状态")
        status2 = curRec.value("发送状态")
        if status2 == "未发送":
            self.pushButton_Delete.setEnabled(True)
            self.pushButton_OpenFeedback.setEnabled(False)
        else:
            self.pushButton_Delete.setEnabled(False)
            if status1 == "未反馈":
                self.pushButton_OpenFeedback.setEnabled(False)
                self.pushButton_Concel.setEnabled(True)
            else:
                self.pushButton_OpenFeedback.setEnabled(True)
                self.pushButton_Concel.setEnabled(False)

        self.do_showInfo(curRec)



    def do_doubleclicked(self):
        if not self.Frame.isHidden():
            self.Frame.hide()
        curRecNo = self.userdatabase.selModel.currentIndex().row()
        curRec = self.userdatabase.tabModel.record(curRecNo)
        if curRec.value("反馈状态") == "未反馈":
            path = os.getcwd()
            if curRec.value("sortrank") == 0:
                filepath = "{}{}".format(path, "\\TempFolderSend\\")
            elif curRec.value("sortrank") == 2:
                filepath = "{}{}".format(path, "\\FolderSend\\")
            os.startfile(filepath)
            self.pushButton_Delete.setEnabled(False)
            self.pushButton_Concel.setEnabled(False)
            self.userdatabase.tabModel.setSort(13, Qt.AscendingOrder)
            self.userdatabase.tabModel.select()
        else:
            self.do_OpenFeedback()
        self.pushButton_OpenFile.setFocus()


    def do_showInfo(self,curRec):

        banklist1 = curRec.value("查询银行")
        banklist2 = curRec.value("未反馈银行")
        bankinfoEx = curRec.value("短消息")
        b1num = len(banklist1.split("、"))
        b2num = len(banklist2.split("、"))
        # print(type(banklist2))
        if banklist1:
            if banklist1 == banklist2:
                bankinfo2 = "目前没有银行反馈信息。"
            else:
                if banklist2 == "":
                    bankinfo2 = "目前所有银行均已反馈。"
                else:
                    bankinfo2 = "目前有{}家银行未反馈：{}。".format(b2num, banklist2)

            if bankinfoEx == "":
                self.textBrowser_BankInfo.setText("此查询涉及{}家银行：{},{}".format(b1num, banklist1, bankinfo2))
            else:
                self.textBrowser_BankInfo.setText("此查询涉及{}家银行：{},{}附加信息:{}。".format(b1num, banklist1, bankinfo2, bankinfoEx))
        else:

            self.textBrowser_BankInfo.setText(bankinfoEx)

    def CMD_Process(self, header_bytes, sk):
        path = os.getcwd()
        header_json = header_bytes.decode('utf-8')
        header_dic = json.loads(header_json)
        cmd = header_dic['CMD']
       # print("deal the received CMD:{}".format(cmd))
        self.do_message("--------------------------------------------------", "#FFFFFF")

        self.do_message("收到指令{}，处理中......".format(cmd), "#FFFFFF")
        # 撤销成功后删除记录和文件
        if "ConcelSuccess" in cmd:
            i = cmd.split('$')
            os.remove("{}{}{}{}".format(path, "\\FolderSend\\", i[2], ".json"))
            fileName_list = os.listdir("{}{}".format(path, "\\FolderSend\\"))
            for f in fileName_list:
                if i[2] in f:
                    os.remove("{}{}{}".format(path, "\\FolderSend\\", f))
                    break
            for n in range(self.userdatabase.tabModel.rowCount()):
                curRecNo = self.userdatabase.tabModel.record(n)
                if curRecNo.value("查询文件编号") == i[2]:
                    self.userdatabase.tabModel.removeRow(n)
                    self.userdatabase.tabModel.submitAll()
                    self.userdatabase.tabModel.setSort(13, Qt.AscendingOrder)
                    self.userdatabase.tabModel.select()
                    break
            self.do_message("编号{}的查询撤销成功！".format(i[2]), "#77FF00")
            self.pushButton_Concel.setEnabled(False)
            curRecNo = self.userdatabase.selModel.currentIndex().row()
            self.userdatabase.mapper.setCurrentIndex(curRecNo)

        elif "ConcelFailed" in cmd:
            i = cmd.split('$')
            self.do_message("编号{}的查询无法撤销！".format(i[2]), "#77FF00")
            self.pushButton_Concel.setEnabled(False)



        # 系统信息显示不在线用户的情况
        elif "$UserIsNotAlive$" in cmd:
            i = cmd.split('$')
            self.do_message("协助单位当前不在线，查询文书已保存在服务器发送缓存中！", "#77FF00")

        elif "$HereIsNewFile$" in cmd:
            i = cmd.split('$')
            self.do_message("你有新的反馈，共计{}个文件，请查收！".format(i[2]), "#77FF00")
            self.pushButton_ReceiveFile.setEnabled(True)
            self.do_showtip(self.pushButton_ReceiveFile, self.lineEdit_Tip_receive, i[2])
            self.num_newfile = int(i[2])

        elif cmd == "$NoNewFile$":
            self.do_message("没有新的反馈！", "#FFFFFF")
            self.pushButton_ReceiveFile.setEnabled(False)
            self.do_showtip(self.pushButton_ReceiveFile, self.lineEdit_Tip_receive, 0)
            self.userdatabase.tabModel.setSort(13, Qt.AscendingOrder)
            self.userdatabase.tabModel.select()
            self.num_left = 0
            self.num_newfile =0
            time.sleep(0.5)
            progress.hide()

            # 拼接文件
            # (filepath, tempfilename) = os.path.split(filename);
            # (shotname, extension) = os.path.splitext(tempfilename)
            fileid = []
            filedic = {}
            filelist = os.listdir(".\\TempFolderReceive\\")
            # print("filelist is {}".format(filelist))
            for f in filelist:
                if ".json" in f:
                    (shotname, extension) = os.path.splitext(f)
                    fileid.append(shotname)
            #     print("fileid is {}".format(fileid))
            for id in fileid:
                # print("id is {}".format(id))
                t = []
                for f in filelist:
                    #  print("f is {}".format(f))
                    if (id in f) and (".json" not in f):
                        # print("t is {}".format(t))
                        t.append(f)
                filedic[id] = t
            #  print("filedic is {}".format(filedic))

            for k in filedic.keys():
                (shotname, extension) = os.path.splitext(filedic[k][0])
                outfile = open((".\\FolderReceive\\{}{}".format(k, extension)), 'wb')
                for file in filedic[k]:
                    infile = open((".\\TempFolderReceive\\{}".format(file)), 'rb')
                    data = infile.read()
                    outfile.write(data)
                    infile.close()
                outfile.close()

            for f in filelist:
                os.remove(".\\TempFolderReceive\\{}".format(f))

            filelist = os.listdir(".\\FolderReceive\\")
            for f in filelist:
                if ".json" in f:
                    orgfile = "{}{}{}".format(path, "\\FolderReceive\\", f)
                    dstfile = "{}{}{}".format(path, "\\FolderReceive\\json\\", f)
                    shutil.copyfile(orgfile, dstfile)
                    os.remove(orgfile)

        elif cmd == "$ServerIsReadyToAccept$":
            server_Address = tuple(header_dic["MainServerTempAdd"])
            user_Name =header_dic["user_name"]
            filelist = os.listdir(".\\TempFolderSend\\")
            if filelist:
                cmd = "${}$IsReadyToSendFile$".format(user_Name)
                try:
                    user_send(self,server_Address, cmd, filelist)
                    self.num_left = self.num_left + 1
                    progress.progressBarValue.emit("发送", self.num_newfile, self.num_left)
                    #user_send_File(self, server_Address, filelist)
                except Exception as e:
                    self.do_message( "向服务器发送文件失败：{}".format(e), "#FFFFFF")
            else:
                self.num_newfile = 0
                self.num_left = 0
                progress.hide()
                try:
                    user_send(self, server_Address, "$JwIsEnd$", [])
                except Exception as e:
                    self.do_message("向服务器发送文件失败：{}".format(e), "#FFFFFF")
        elif cmd == "$ServerIsReadyToSend$":
            self.num_left = self.num_left + 1
            progress.progressBarValue.emit("接收", self.num_newfile, self.num_left)
            user_receive_File(self, sk , header_dic)
            time.sleep(0.1)
            user_send(self, tuple(header_dic["MainServerTempAdd"]), "$WeNeedFileFromJW$", [])
        self.do_message("指令{}处理完毕。".format(cmd), "#FFFFFF")
    def closeEvent(self, event):
        with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
          data = json.load(f)
          f.close()
        data["file_name"] = "userdb.db3"
        data["file_num"] = 1
        path = os.getcwd()
        file = "{}\\{}".format(path, "userdb.db3")
        data["file_size"] = os.path.getsize(file)
        with open(file, 'rb') as ff:
            filedata = ff.read()
        data["CMD"] = "${}$down$".format(data["user_name"])
        header_json = json.dumps(data)
        header_bytes = header_json.encode('utf-8')
        #print(header_bytes)
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.do_message("正在备份数据库文件.......", "#FFFFFF")
        try:
            sk.connect(tuple(data["MainServerTempAdd"]))
            sk.send(struct.pack('i', len(header_bytes)))  # 将报头长度转化为int类型，而int类型为4个字节，所以发送固定长度4个字节
            sk.send(header_bytes)
            if data["file_size"]:
                sk.sendall(filedata)
            sk.close()
        except Exception as e:
            self.do_message("备份失败，原因：{}，请稍后再试。".format(e), "#FFFFFF")
        else:
            self.do_message("数据库文件备份成功！", "#FFFFFF")

        with open('info.log', 'a') as f:
            text = self.textBrowser_Info.toPlainText()
            f.write(text)
            f.close()
        time.sleep(1)
        os._exit(0)

    def do_message(self, message, fontcolor):
        time.sleep(0.1)
        timeStamp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        self.textBrowser_Info.append("<font color=\"{}\">".format(fontcolor)
                                     + "{} # {}".format(timeStamp, message)
                                     + "</font> ")
        self.textBrowser_Info.moveCursor(self.textBrowser_Info.textCursor().End)


def server_Process():
    with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
        data = json.load(f)
        f.close()
    #userserver_Address = tuple(data["UserServer"])
    user_ip = data["user_ip"]
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((user_ip, 0))  # 绑定套接字到本机的网络地址,端口随机
    user_ip,port = sock.getsockname()
    data["user_port"] = port
    data["UserServer"][0]= user_ip
    data["UserServer"][1] = port
    with open('newNetInfo.json', 'w') as ff:
        json.dump(data, ff)
        ff.close()
    sock.listen(4)  # 10表示最大连接数
    while True:
        sk, sockname = sock.accept()
        # 1收报头长度
        obj = sk.recv(4)
        header_size = struct.unpack('i', obj)[0]
        # 2接收报头
        header_bytes = sk.recv(header_size)
        win.CMD_Process(header_bytes, sk)
        sk.close()
if __name__ == '__main__':
    banklist = {}
    banklist_back = {}
    folder = os.path.exists("TempFolderSend")
    if not folder:                               #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("TempFolderSend")            #makedirs 创建文件时如果路径不存在会创建这个路径
    folder = os.path.exists("TempFolderReceive")
    if not folder:
        os.makedirs("TempFolderReceive")
    folder = os.path.exists("FolderSend")
    if not folder:                               #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("FolderSend") 
    folder = os.path.exists("FolderReceive")
    if not folder:                               #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("FolderReceive")

    folder = os.path.exists("FolderReceive\\json\\")
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs("FolderReceive\\json\\")

    app = QtWidgets.QApplication(sys.argv)
    progress = MyProgress()
    progress.progressBarValue.connect(progress.do_myprocress_show)
    win = MainForm()
    dlg = MyDialog()
    dlg.exec_()
    serverStart = Thread(target=server_Process, args=())
    serverStart.start()
    time.sleep(0.2)
    with open('newNetInfo.json', 'r') as f:  # 打开文件用于读
        data = json.load(f)
        f.close()
    #print("server tem address is:{}".format(data["MainServerTempAdd"]))
    win.do_message("===================New Session====================", "#FFFFFF")
    win.do_message("正在查询是否有新的反馈........", "#FFFFFF")
    user_send(win, tuple(data["MainServerTempAdd"]), "$WeNeedFileFromOT$",[])

    sys.exit(app.exec_())
