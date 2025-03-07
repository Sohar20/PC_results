# -*- coding: utf-8 -*-

import psutil, keyboard, threading, os, platform
from plyer.platforms.win.notification import instance as notification_instance

from time import sleep, time
import subprocess as sp


import matplotlib.pyplot as plt
import pickle as pkl
from gui_1 import Ui_MainWindow
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox
import matplotlib.rcsetup as rcsetup

def push(title, message):
    plt = platform.system()
    if plt == "Darwin":
        command = '''
        osascript -e 'display notification "{message}" with title "{title}"'
        '''
    elif plt == "Linux":
        command = f'''
        notify-send "{title}" "{message}"
        '''
    elif plt == "Windows":
        notification_instance().notify(title=title, message=message)
        return
    else:
        return
    os.system(command)

def get_gpu_usage():
    val = sp.run(['powershell', '-Command', gpu_usage_cmd], capture_output=True).stdout.decode("ascii")
    return round(float(val.strip().replace(',', '.')), 1)

def get_cpu_usage():
    l = psutil.cpu_percent()
    if len(cpu)==0:
        return l
    else:
        return (cpu[-1]+l)//2

def build_graph():
    global cpu, ram, gpu, x
    if cpu:
        fig, ax = plt.subplots()
        ax.plot(x, cpu, color='#38D999')
        ax.plot(x, ram, color='#F080FE')
        if -1 not in gpu:
            ax.plot(x, gpu, color='#E9FE80')
        ax.set_ylim(0, 100)
        ax.set_xlim(min(x), max(x))
        fig.patch.set_facecolor('#414164')
        ax.set_facecolor('#414164')
        ax.spines['left'].set_color('#ffffff')
        ax.spines['right'].set_color('#ffffff')
        ax.yaxis.label.set_color('#ffffff')
        ax.tick_params(axis='y', colors='#ffffff')
        ax.spines['bottom'].set_color('#ffffff')
        ax.spines['top'].set_color('#ffffff')
        ax.xaxis.label.set_color('#ffffff')
        ax.tick_params(axis='x', colors='#ffffff')
        ax.set_xlabel("Time, seconds", fontsize=15, color='white')
        ax.set_ylabel("Usage, %", fontsize=15, color='white')
        ax.grid()
        if -1 not in gpu:
            plt.legend(['CPU', 'RAM', 'GPU'])
        else:
            plt.legend(['CPU', 'RAM'])
        fig.suptitle(ui.title_edt.text(), fontsize=30, color='white')
        plt.show()

def clear_focus(object: QtWidgets.QLineEdit):
    if object.hasFocus():
        a = object.text()
        a = a[:-1]
        object.setText(a)
        object.setFocus(False)

def grey_btn(object: QtWidgets.QPushButton):
    object.setEnabled(False)
    object.setStyleSheet("QPushButton{\n"
"border:2px solid rgb(160, 160, 178);\n"
"font: 57 12pt \"Dotum\";\n"
"color:rgb(160, 160, 178);\n"
"}")
    
def ungrey_btn(object: QtWidgets.QPushButton):
    object.setEnabled(True)
    object.setStyleSheet("QPushButton{\n"
"border:2px solid white;\n"
"font: 57 12pt \"Dotum\";\n"
"color:white;\n"
"}\n"
"QPushButton:Hover{\n"
"border:2px solid rgb(240, 128, 254);\n"
"font: 57 12pt \"Dotum\";\n"
"color:white;\n"
"}\n"
"QPushButton:pressed{\n"
"border:2px solid rgb(56, 217, 153);\n"
"font: 57 12pt \"Dotum\";\n"
"color:rgb(56, 217, 153);\n"
"}")

def change_to_on():
    global cpu, gpu, ram, x, i, mon_on, start, timer_time
    global flag, timer_on
    flag = False
    error = QMessageBox()
    error.setWindowTitle('error')
    error.setIcon(QMessageBox.Warning)
    clear_focus(ui.title_edt)
    clear_focus(ui.minutes_edt)
    clear_focus(ui.seconds_edt)

    if timer_on:
        minutes = ui.minutes_edt.text().replace('p', '')
        if len(minutes)==0:
            minutes=0
        ui.minutes_edt.setText(str(minutes))

        try:
            minutes = int(minutes)
        except:
            if not keys:
                error.setText('Value of minutes should be an intenger!')
                error.exec_()
            else:
                ui.warn_lbl.setText('Value of minutes should be an intenger!')
                push('Unable to start monitoring', 'Value of minutes should be an intenger!')
            ui.seconds_edt.setEnabled(True)
            ui.minutes_edt.setEnabled(True)
            flag = True
            return
        
        seconds = ui.seconds_edt.text().replace('p', '')
        if len(seconds)==0:
            seconds=0
        ui.seconds_edt.setText(str(seconds))
        try:
            seconds = int(seconds)
        except:
            if not keys:
                error.setText('Value of seconds should be an intenger!')
                error.exec_()
            else:
                ui.warn_lbl.setText('Value of seconds should be an intenger!')
                push('Unable to start monitoring', 'Value of seconds should be an intenger!')
            ui.seconds_edt.setEnabled(True)
            ui.minutes_edt.setEnabled(True)
            flag = True
            return
        timer_time = minutes*60+seconds
        if timer_time <=3:
            if not keys:
                error.setText('Time of the timer should be more than 3 seconds')
                error.exec_()
            else:
                ui.warn_lbl.setText('Time of the timer should be more than 3 seconds')
            ui.seconds_edt.setEnabled(True)
            ui.minutes_edt.setEnabled(True)
            flag=True
            return

    ui.warn_lbl.setText('')
    cpu=[]
    gpu=[]
    ram=[]
    x=[]
    i=1
    ui.start_btn.setText('Stop monitoring (Alt + S)')
    if keys:
        push('Monitoring started', 'Press Alt+S to stop it')
    ui.info_lbl.setText('Monitoring started')
    mon_on = True
    clear_focus(ui.title_edt)
    clear_focus(ui.title_edt)
    grey_btn(ui.open_btn)
    grey_btn(ui.display_btn)
    grey_btn(ui.save_btn)
    sleep(2)
    ui.info_lbl.setText('')
    ui.start_btn.setEnabled(True)
    flag = True

def change_to_off():
    global flag, keys
    flag = False

    ui.start_btn.setEnabled(False)
    ungrey_btn(ui.open_btn)
    ungrey_btn(ui.display_btn)
    ungrey_btn(ui.save_btn)
    global mon_on, start
    ui.start_btn.setText('Start monitoring (Alt + P)')
    if keys:
        push('Monitoring stopped', 'Press Alt+P to start it')
    mon_on = False
    clear_focus(ui.title_edt)

    ui.info_lbl.setText('Monitoring stopped')
    sleep(2)
    ui.info_lbl.setText('')
    ui.start_btn.setEnabled(True)
    flag = True

def timer_checked():
    global timer_on

    if not ui.timer_chb.isChecked():
        ui.minutes_edt.setEnabled(False)
        ui.seconds_edt.setEnabled(False)
        ui.minutes_edt.setStyleSheet("font: 57 12pt \"Dotum\";\n"
"color:rgb(128, 128, 128);\n"
"border:1px solid rgb(128, 128, 128);")
        ui.minutes_lbl.setStyleSheet("font: 57 12pt \"Dotum\";\n"
"color:rgb(128, 128, 128);")
        
        ui.seconds_edt.setStyleSheet("font: 57 12pt \"Dotum\";\n"
"color:rgb(128, 128, 128);\n"
"border:1px solid rgb(128, 128, 128);")
        ui.seconds_lbl.setStyleSheet("font: 57 12pt \"Dotum\";\n"
"color:rgb(128, 128, 128);")
        timer_on=False

    elif ui.timer_chb.isChecked():
        ui.minutes_edt.setEnabled(True)
        ui.seconds_edt.setEnabled(True)
        ui.minutes_edt.setStyleSheet("font: 57 12pt \"Dotum\";\n"
"color:white;\n"
"border:1px solid rgb(255, 255, 255);")
        ui.minutes_lbl.setStyleSheet("font: 57 12pt \"Dotum\";\n"
"color:white;")
        
        ui.seconds_edt.setStyleSheet("font: 57 12pt \"Dotum\";\n"
"color:white;\n"
"border:1px solid rgb(255, 255, 255);")
        ui.seconds_lbl.setStyleSheet("font: 57 12pt \"Dotum\";\n"
"color:white;")
        timer_on=True
        

def strt_mon():
    global mon_on, timer_on, ui, cpu, ram, gpu, x, i, flag, keys
    flag = True

    while not ui.title_lbl.isVisible():
        pass

    keys = False
    while True:
        keys = False
        if not flag:
            sleep(0.5)
            continue
        if keyboard.is_pressed('Alt + P') and not mon_on:
            keys = True
            ui.seconds_edt.setEnabled(False)
            ui.minutes_edt.setEnabled(False)
            change_to_on()
            sleep(2)
            continue
        if mon_on and timer_on:
            res = str(round(timer_time-(time()-start), 2))
            fract=res.split('.')[-1]
            if len(fract)==1:
                res+='0'
            ui.time_lbl.setText(f'Timer: {res} seconds')
        else:
            ui.time_lbl.setText('')
        if (keyboard.is_pressed('Alt + S') or (timer_on and time()-start>=timer_time)) and mon_on:
            keys=True
            change_to_off()

        if not ui.title_lbl.isVisible():
            break
        sleep(0.03)

def pressed_start():
    global start
    if mon_on:
        tr_change = threading.Thread(target=change_to_off)
    else:
        tr_change = threading.Thread(target=change_to_on)
    tr_change.run()

def open_graph():

    error = QMessageBox()
    error.setWindowTitle('error')
    error.setIcon(QMessageBox.Warning)
    fileName = QFileDialog.getOpenFileName(None, "Open Document", "", "Text files *.pkl")
    print(fileName)
    if fileName[0]:
        with open(fileName[0], 'rb') as f:
            data=pkl.load(f)
        for key in ('cpu', 'ram', 'gpu', 'x', 'title'):
            if key not in data:
                error.setText('Data cannot be read')
                error.exec_()
                return
        
        cpu = data['cpu']
        gpu = data['gpu']
        ram = data['ram']
        x = data['x']
        title = data['title']
        
        fig, ax = plt.subplots()
        ax.plot(x, cpu, color='#38D999')
        ax.plot(x, ram, color='#F080FE')
        if -1 not in gpu:
            ax.plot(x, gpu, color='#E9FE80')
        ax.set_ylim(0, 100)
        ax.set_xlim(min(x), max(x))
        fig.patch.set_facecolor('#414164')
        ax.set_facecolor('#414164')
        ax.spines['left'].set_color('#ffffff')
        ax.spines['right'].set_color('#ffffff')
        ax.yaxis.label.set_color('#ffffff')
        ax.tick_params(axis='y', colors='#ffffff')
        ax.spines['bottom'].set_color('#ffffff')
        ax.spines['top'].set_color('#ffffff')
        ax.xaxis.label.set_color('#ffffff')
        ax.tick_params(axis='x', colors='#ffffff')
        ax.set_xlabel("Time, seconds", fontsize=15, color='white')
        ax.set_ylabel("Usage, %", fontsize=15, color='white')
        ax.grid()
        fig.suptitle(title, fontsize=30, color='white')
        if -1 not in gpu:
            plt.legend(['CPU', 'RAM', 'GPU'])
        else:
            plt.legend(['CPU', 'RAM'])
        plt.show()

def save_graph():
    file = QtWidgets.QFileDialog.getSaveFileName(parent=None, caption="Saving", 
          directory=os.getcwd(), 
          filter="All (*);;pkl (*.pkl)", 
          initialFilter="pkl (*.pkl)")
    file_name = file[0]
    if file_name != "":
        with open(file_name, 'wb') as f:
            pkl.dump({'cpu': cpu, 'gpu': gpu, 'ram': ram, 'x': x, 'title': ui.title_edt.text()}, f)

def main():
    global timer_time, timer_on, saving, cpu, ram, gpu
    global x, mon_on, ui, gpu_in, start, gpu_usage_cmd
    gpu_usage_cmd = r'(((Get-Counter "\GPU Engine(*engtype_3D)\Utilization Percentage").CounterSamples | where CookedValue).CookedValue | measure -sum).sum'
    start=time()
    gpu_in = True
    saving = True
    timer_on = True
    timer_time = 60

    if not gpu_in:
        ui.gpu_warn.setText('GPU monitoring is unavailable on your device')

    mon_on = False
    cpu=[]
    ram=[]
    gpu=[]
    x=[]
    i=1
    while not ui.title_lbl.isVisible():
        pass

    while True:
        c = get_cpu_usage()
        r = psutil.virtual_memory().percent
        if gpu_in:
            g = get_gpu_usage()
        else:
            sleep(1)
            g = -1
        
        try:
            ui.cpu_lbl.setText(f'CPU: {c}%')
            ui.gpu_lbl.setText(f'GPU: {g}%')
            ui.ram_lbl.setText(f'RAM: {r}%')
        except:
            continue

        if not ui.title_lbl.isVisible():
            break
        

        if mon_on:
            if i==1:
                start = time()
            cpu.append(c)
            ram.append(r)
            gpu.append(g)
            x.append(round(time()-start, 1))
            i+=1
        
        if not mon_on and len(cpu):
            if len(cpu) and len(gpu) and len(ram):
                if len(cpu)>len(gpu):
                    cpu.pop()
                if len(ram)>len(gpu):
                    ram.pop()
            i=1 
    


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    back_tr = threading.Thread(target=main)
    back_tr.start()

    tr1 = threading.Thread(target=strt_mon)
    tr1.start()

    
    ui.open_btn.clicked.connect(open_graph)
    ui.display_btn.clicked.connect(build_graph)
    ui.start_btn.clicked.connect(pressed_start)
    ui.save_btn.clicked.connect(save_graph)
    ui.timer_chb.clicked.connect(timer_checked)


    MainWindow.setWindowTitle('PC results')
    MainWindow.show()
    sys.exit(app.exec_())