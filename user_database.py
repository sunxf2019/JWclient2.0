# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 23:18:05 2020

@author: Sharksunxf
"""
import os , sys
import time
import shutil
import re
import json
from PyQt5.QtWidgets import QMessageBox, QDataWidgetMapper, QHeaderView
from PyQt5.QtCore    import Qt, QItemSelectionModel, QModelIndex
from PyQt5.QtSql     import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlRecord, QSqlQuery
from PyQt5.QtGui     import QBrush, QColor


class MySqlTableModel(QSqlTableModel, QSqlDatabase):
    def __init__(self, parent = QSqlTableModel, db = QSqlDatabase()):
        super(MySqlTableModel, self).__init__()

    def data(self, index, role):
        curRecNo = index.row()
        sortrank = QSqlTableModel.data(self, QSqlTableModel.index(self, curRecNo, 13))
        # 颜色等级分三级：
        # 1、红色：新的任务：      未发送的新查询和未读取的新反馈
        # 2、黄色：等待反馈的任务：已发送未反馈的查询和已读取的部分反馈
        # 3、灰色：结束归档的任务：已读取的全部反馈
        if role == Qt.BackgroundRole:
            if sortrank == 0:
                return QBrush(QColor(250, 250, 250))
            elif sortrank == 1:
                return QBrush(QColor(255, 80, 0))        # 等级1
            elif sortrank == 2:
                return QBrush(QColor(255, 215, 0))        # 等级2
            else:
                return QBrush(QColor(200, 200, 200))      # 等级3
        # 设置单元格居中显示
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return QSqlTableModel.data(self, index, role)

    def user_Database_init(self, win):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("userdb.db3")
        self.db.close()
        if self.db.open():
            self.do_openTable(win)
        else:
            QMessageBox.critical(win,"错误", "打开userdb.db3文件失败！")

    def do_openTable(self, win):
        self.win =win
        self.tabModel = MySqlTableModel(self, self.db)
        self.tabModel.setTable("UserData")
        self.tabModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.tabModel.setSort(self.tabModel.fieldIndex("序号"), Qt.DescendingOrder)
        if self.tabModel.select()==False:
            QMessageBox.critical(self.win,"错误", "打开数据表UserData失败！")
            self.db.close()
            return
        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(self.tabModel)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
        self.mapper.addMapping(win.LineEdit_StartTime, self.tabModel.fieldIndex("查询时间"))
        self.mapper.addMapping(win.LineEdit_AskFileName, self.tabModel.fieldIndex("查询文件名称"))
        self.mapper.addMapping(win.LineEdit_User, self.tabModel.fieldIndex("申请单位"))
        self.mapper.addMapping(win.LineEdit_What, self.tabModel.fieldIndex("查询内容"))
        self.mapper.addMapping(win.LineEdit_FileID, self.tabModel.fieldIndex("查询文件编号"))
        self.mapper.addMapping(win.LineEdit_FeedbackTime, self.tabModel.fieldIndex("反馈时间"))
        self.mapper.addMapping(win.LineEdit_FeedbackFile, self.tabModel.fieldIndex("反馈文件名称"))
        self.mapper.addMapping(win.LineEdit_FeedbackStatus, self.tabModel.fieldIndex("反馈状态"))
        self.mapper.addMapping(win.LineEdit_Who, self.tabModel.fieldIndex("对象名称"))
        self.mapper.addMapping(win.LineEdit_PersonNum, self.tabModel.fieldIndex("人数"))
        self.mapper.addMapping(win.LineEdit_UnitNum, self.tabModel.fieldIndex("单位数"))
        self.mapper.addMapping(win.LineEdit_SendSw, self.tabModel.fieldIndex("发送状态"))
        self.selModel = QItemSelectionModel(self.tabModel)
        win.tableView_Data.setModel(self.tabModel)
        win.tableView_Data.setSelectionModel(self.selModel)
        self.tabModel.setSort(13, Qt.AscendingOrder)
        self.tabModel.select()
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex('查询文件名称'), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex('单位数'), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex('人数'), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex('反馈状态'), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex('发送状态'), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex('序号'), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex('sortrank'), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("查询银行"), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("未反馈银行"), True)
        win.tableView_Data.setColumnHidden(self.tabModel.fieldIndex("短消息"), True)
            # 根据第2至12列每列内容设置列宽
        for i in range(1, 11):
            win.tableView_Data.resizeColumnToContents(i)

            # 设置第2、3、11列列宽为自适应
        win.tableView_Data.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        win.tableView_Data.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        win.tableView_Data.horizontalHeader().setSectionResizeMode(10, QHeaderView.Stretch)
        win.tableView_Data.horizontalHeader().setStyleSheet(
                "QHeaderView::section{ font-size : 10pt; height:26px;border-top:1px solid gray;border-bottom:1px solid gray;"
                "border-right:1px solid gray;background:#CFCFCF;}")
        win.tableView_Data.setStyleSheet("selection-background-color:#76EE00")

    #添加记录，最新的记录在最上面
    def do_addRecord(self, dlginfo):
        self.tabModel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.tabModel.insertRow(0, QModelIndex())
        curIndex = self.tabModel.index(0, 1)
        currow=curIndex.row()
        # dlgInfo = [dlgFilename, dlgWhat, dlgUser, dlgWho, dlgPnum, dlgUnum, dlgBankCode, dlgBankCodeBack, dlgSms]

        # 生成查询文件编号
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        # 命名示例[银行流水]20210518金湖县@张明
        fileID = "[{}]{}{}@{}".format(dlginfo[1], str(date),dlginfo[2],dlginfo[3])

        # 生成含查询文件信息的json文件
        with open('fileInfo.json', 'r', encoding='UTF-8') as f:  # 打开文件用于读
            data = json.load(f)
            f.close()
        data["查询文件编号"] = fileID
        data["查询时间"] = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        data["申请单位"] = dlginfo[2]
        data["查询内容"] = dlginfo[1]
        data["对象名称"] = dlginfo[3]
        data["人数"] = dlginfo[4]
        data["单位数"] = dlginfo[5]
        string =""
        for i in range(len(dlginfo[6])):
            string = string + dlginfo[6][i]+"、"
        data["查询银行"] = string.rstrip("、")
        data["未反馈银行"] = data["查询银行"]
        data["短消息"] = dlginfo[8]

        # 存入数据库
        self.tabModel.setData(self.tabModel.index(currow, 0), self.tabModel.rowCount())  # 添加序号
        self.tabModel.setData(self.tabModel.index(currow, 1), data["查询文件编号"])
        self.tabModel.setData(self.tabModel.index(currow, 2), dlginfo[0])                # 添加查询文件名称
       # self.tabModel.setData(self.tabModel.index(currow, 3), date)                      # 添加查询时间
        self.tabModel.setData(self.tabModel.index(currow, 4), data["申请单位"] )                # 添加申请单位
        self.tabModel.setData(self.tabModel.index(currow, 5), data["查询内容"])                # 添加查询内容
        self.tabModel.setData(self.tabModel.index(currow, 6), data["对象名称"])                # 添加查询对象
        self.tabModel.setData(self.tabModel.index(currow, 7), data["人数"])                # 添加查询人数
        self.tabModel.setData(self.tabModel.index(currow, 8), data["单位数"])                # 添加查询单位数
        self.tabModel.setData(self.tabModel.index(currow, 11), "未反馈")                   # 添加反馈状态
        self.tabModel.setData(self.tabModel.index(currow, 12), "未发送")
        self.tabModel.setData(self.tabModel.index(currow, 13), 0)
        self.tabModel.setData(self.tabModel.index(currow, 14), data["查询银行"])  # 添加查询银行列表
        self.tabModel.setData(self.tabModel.index(currow, 15), data["未反馈银行"])  # 添加未反馈银行列表
        self.tabModel.setData(self.tabModel.index(currow, 16), data["短消息"])  # 添加短消息
        res = self.tabModel.submitAll()
        if res:
            orignalFeFileName_base = os.path.basename(dlginfo[0])
            f, ftype = os.path.splitext(orignalFeFileName_base)
            newFileName = "{}{}".format(fileID, ftype)
            self.do_rename_copyFile(dlginfo[0], newFileName)

            with open('fileInfo.json', 'w', encoding='UTF-8') as f:
                json.dump(data, f)
                f.close()
            jsonFileName = "{}{}".format(fileID, ".json")
            self.do_rename_copyFile('fileInfo.json', jsonFileName)

            self.tabModel.setSort(13, Qt.AscendingOrder)
            self.tabModel.select()
        else:
            QMessageBox.critical( self.win, "错误", "添加记录失败：\n"+self.tabModel.lastError().text())
    def do_rename_copyFile(self,oldfilename,newfilename):
        path = os.getcwd()
        dstDir = "{}{}".format(path, "\\FolderSend\\")
        dstfile=dstDir+newfilename
        shutil.copyfile(oldfilename, dstfile)

        kilobytes = 1024
        megabytes = kilobytes * 1000
        chunksize = int(15 * megabytes)  # default chunksize
        dstDir_temp = "{}{}".format(path, "\\TempFolderSend\\")
        (filepath, tempfilename) = os.path.split(newfilename);
        (shotname, extension) = os.path.splitext(tempfilename)
        # os.remove(os.path.join(todir, fname))
        partnum = 0
        filesize = os.path.getsize(oldfilename)
        inputfile = open(oldfilename, 'rb')  # open the fromfile
        if filesize > chunksize:
            while True:
                chunk = inputfile.read(chunksize)
                if not chunk:
                    break
                partnum += 1
                filename = os.path.join(dstDir_temp , (shotname + '@%03d' % partnum + extension))
                fileobj = open(filename, 'wb')  # make partfile
                fileobj.write(chunk)  # write data into partfile
                fileobj.close()
        else:
            dstfile=dstDir_temp+newfilename
            shutil.copyfile(oldfilename, dstfile)



    def do_changeAndRecord(self, file):
        if self.tabModel.rowCount() == 0:
            return
        else:
            for i in range(self.tabModel.rowCount()):
                rec = self.tabModel.record(i)
                if rec.value("查询文件编号") in file:
                    timeStamp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
                    self.tabModel.setData(self.tabModel.index(i, 3), timeStamp)  # 记录查询发起时间
                    self.tabModel.setData(self.tabModel.index(i, 12), "已发送")
                    self.tabModel.setData(self.tabModel.index(i, 13), 2)
                    break
            res = self.tabModel.submitAll()
            self.tabModel.setSort(13, Qt.AscendingOrder)
            self.tabModel.select()
            if not res:
                QMessageBox.warning(self.win,u"错误", u"错误！\n" + self.tabModel.lastError().text())
                self.tabModel.revertAll()
# 处理反馈文书
    def do_dealFeedbackFile(self, file):
        if self.tabModel.rowCount() == 0:
            return
        else:
            for i in range(self.tabModel.rowCount()):
                rec = self.tabModel.record(i).value("查询文件编号")
               # print(rec)
                if rec in file:
                    file = ".\\TempFolderReceive\\{}".format(file)
                    #print("the file is {}".format(file))
                    with open(file, 'r', encoding='UTF-8') as f:  # 打开文件用于读
                        data = json.load(f)
                        f.close()
                    self.tabModel.setData(self.tabModel.index(i, 10), data["反馈文件名称"])                  # 添加反馈文件名
                    timeStamp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))  # 添加反馈时间
                    self.tabModel.setData(self.tabModel.index(i, 9), timeStamp)
                    self.tabModel.setData(self.tabModel.index(i, 13), 1)
                    f, ftype = os.path.splitext(file)
                    flist = re.split('-', f)

                    if "P" in flist[1]:
                        self.tabModel.setData(self.tabModel.index(i, 11), "部分反馈")
                    elif "E" in flist[1]:
                        self.tabModel.setData(self.tabModel.index(i, 11), "全部反馈")
                    self.tabModel.setData(self.tabModel.index(i, 15), data["未反馈银行"])
                    self.tabModel.setData(self.tabModel.index(i, 16), data["短消息"])
                    break

            res = self.tabModel.submitAll()
            if not res:
                QMessageBox.warning(self.win, u"错误", u"错误！\n" + self.tabModel.lastError().text())
                self.tabModel.revertAll()






