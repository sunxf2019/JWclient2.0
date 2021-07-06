# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 14:57:06 2020

@author: Sharksunxf
"""
import socket
import struct
import json
import os
# user_database import do_changeAndRecord

def user_send(self, server_Address, cmd, filelist):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sk.connect(server_Address)
    except Exception as e:
        self.do_message("发送失败，原因：{}".format(e),"#FFFFFF")
        return False
    else:

        with open('newNetInfo.json', 'r') as ff:  # 打开文件用于读
            data = json.load(ff)
            ff.close()
        if filelist != []:
            for f in filelist:
                data["file_name"] = f
                data["file_num"] = 1
                path = os.getcwd()
                file = "{}{}{}".format(path, "\\TempFolderSend\\", f)
                data["file_size"] = os.path.getsize(file)
                with open(file, 'rb') as ff:
                    filedata = ff.read()
                break
        else:
            data["file_name"] = ""
            data["file_num"] = 1
            data["file_size"] = 0
            #filedata = b""
        data["CMD"] = cmd
        header_json = json.dumps(data)
        header_bytes = header_json.encode('utf-8')
            # 2 发送报头长度
        self.do_message("指令{}发送中......".format(cmd), "#FFFFFF")
        try:
            sk.send(struct.pack('i', len(header_bytes)))  # 将报头长度转化为int类型，而int类型为4个字节，所以发送固定长度4个字节
            # 3 发报头
            sk.send(header_bytes)
        except Exception as e:
            self.do_message("指令{}发送失败：{}".format(e, cmd), "#FFFFFF")
            # 4 发真实数据
        else:
            if data["file_size"]:
                self.do_message( "发送查询文书{}........".format(data["file_name"]), "#FFFFFF")
                sk.sendall(filedata)
                os.remove(file)
                self.userdatabase.do_changeAndRecord(f)
        self.do_message("发送完毕。", "#FFFFFF")
        sk.close()

    return True




    

