import os
import socket
import subprocess
import time
import tkinter as tk
import datetime
import threading
import traceback
from PIL import Image, ImageTk
import PySimpleGUI as sg
from OLD_GUI import VRGUI
from OLD_Print import VRPrint
from OLD_GUI import console_window
from OLD_GUI import user_authentication
from OLD_GUI import file_hosting
from OLD_GUI import ask_to_delete_file
from OLD_Redactor import VRRedactor
import paramiko
import sys


def bytes_size_convert(bytes_size):
    bytes_size, suffix_count, suffix = float(bytes_size), 0, ('Bs', 'KB', 'MB', 'GB')
    while bytes_size > 1024. and suffix_count < 3:
        bytes_size = bytes_size / 1024
        suffix_count += 1
    return '{0:.2f} {1}'.format(bytes_size, suffix[suffix_count])


def _authentication():
    user = ''
    first_event = '\r'
    window = VRGUI(GUI_type=user_authentication, title='VaspReader', return_keyboard_events=True).window_return()
    window['-USERNAME-'].update(values=_find_used_usernames())
    while True:
        event, value = window.read()
        if event == first_event:
            first_event = ...
            continue
        else:
            first_event = ...
        if event == sg.WINDOW_CLOSED or 'Esc' in event:
            user = 'break'
            break
        if event == '-AUTHSUBM-' or event == '\r':
            user = value['-USERNAME-']
            if user:
                with open('ALtemP', 'a+b') as temp:
                    temp.seek(0)
                    temp_data = temp.readlines()
                    user_list = [_unmask_string(temp_data[index]) for index in range(len(temp_data))]
                    if user not in user_list:
                        temp.write(bytes(_mask_string(user), encoding='utf8'))
            else:
                user = 'user_do_not_input'
            break
    window.close()
    return user


def _find_used_usernames():
    users = ['']
    try:
        with open('ALtemP', 'r+b') as temp:
            temp_data = temp.readlines()
            if temp_data:
                users = [_unmask_string(temp_str) for temp_str in temp_data]
    except FileNotFoundError:
        pass
    return users


def _mask_string(symbols):
    return '\x00'.join([str(bin(ord(symbol))) for symbol in symbols]) + '\n' if symbols else None


def _unmask_string(symbols):
    return ''.join([chr(int(symb, 2)) for symb in symbols.decode('utf8').split('\n')[0].split('\x00')]) if symbols else None


def _close_ssh(ssh_object):
    try:
        ssh_object.close()
    except:
        pass


class VRConsole(VRGUI, VRPrint):
    def __init__(self, GUI_type=console_window, title='VaspReader', theme='VRGUI'):
        super(VRConsole, self).__init__(GUI_type, title, resizable=True, keep_on_top=False, return_keyboard_events=True, theme=theme)
        VRPrint.__init__(self)
        self.event, self.value = None, None
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.user = _authentication()
        self.last_commands, self.index_com = [''], -1
        self.read_last_commands()
        self.writer = None
        self.start_mainloop = False
        if self.user not in ['break', 'user_do_not_input']:
            self.window.set_title(f'VaspReader ({self.user})')
            self.start_mainloop = True

    def read_last_commands(self):
        with open('commands', 'a+b') as com:
            com.seek(0)
            self.last_commands = com.readlines()
            if self.last_commands:
                self.last_commands = [_unmask_string(command) for command in self.last_commands]

    @ staticmethod
    def write_text_ssh(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write("\r\nSession was interrupted...\r\nPress Enter to leave.")
                sys.stdout.flush()
                break
            sys.stdout.write(data.decode('utf8'))
            sys.stdout.flush()

    def connect_try(self):
        self.ssh.connect('lomonosov2.parallel.ru', username=self.user)
        self.ssh = self.ssh.get_transport().open_session()
        self.ssh.get_pty()
        self.ssh.invoke_shell()
        self.writer = threading.Thread(target=self.write_text_ssh, args=(self.ssh,))
        self.writer.start()
        self.window['-CONSOLEINPUT-'].set_focus(force=True)

    def mainloop(self):
        if self.start_mainloop:
            try:
                self.connect_try()
            except paramiko.ssh_exception.AuthenticationException:
                self.window.close()
                self.print('User not found. Check your username.')
            except paramiko.ssh_exception.SSHException:
                self.window.close()
                self.print('No authentication methods available. Add ssh key to Pegeant to work with console.\n')
            else:
                while True:
                    self.event, self.value = self.window.read()
                    if self.event == sg.WIN_CLOSED:
                        _close_ssh(self.ssh)
                        self.window.close()
                        with open('commands', 'w+b') as com:
                            if len(self.last_commands) > 80:
                                self.last_commands = self.last_commands[-80:]
                            [com.write(bytes(_mask_string(command), encoding='utf8')) for command in self.last_commands]
                        break
                    if self.event == '\r':
                        command = self.value['-CONSOLEINPUT-']
                        if not self.last_commands or command != self.last_commands[-1]:
                            self.last_commands.append(command)
                        self.ssh.send(self.value['-CONSOLEINPUT-'] + '\n')
                        self.index_com = -1
                        self.window['-CONSOLEINPUT-'].update('')
                    if 'Esc' in self.event:
                        _close_ssh(self.ssh)
                        break
                    if 'F1' in self.event:
                        self.window['-CONSOLEINPUT-'].update('squeue -p compute')
                    if 'F2' in self.event:
                        self.window['-CONSOLEINPUT-'].update('squeue -p test')
                    if 'F3' in self.event:
                        self.window['-CONSOLEINPUT-'].update('sbatch -N 14 ompi vasp_gpu')
                    if 'F4' in self.event:
                        self.window['-CONSOLEINPUT-'].update('sbatch -N 7 --tasks-per-node 14 -p test ompi vasp_std')
                    if 'F5' in self.event:
                        self.window['-CONSOLEINPUT-'].update('cd ..')
                    if 'F6' in self.event:
                        self.window['-CONSOLEINPUT-'].update('cd _scratch')
                    if 'Up:' in self.event:
                        try:
                            if self.last_commands:
                                command = self.last_commands[self.index_com]
                                self.window['-CONSOLEINPUT-'].update(command)
                                self.index_com -= 1 if len(self.last_commands) > abs(self.index_com) else 0
                        except:
                            print('Hm... Something wrong.', end='\n\n>> ')
                    if 'Down:' in self.event:
                        try:
                            if self.last_commands:
                                if self.index_com < -1:
                                    self.index_com += 1
                                    command = self.last_commands[self.index_com]
                                else:
                                    command = ''
                                self.window['-CONSOLEINPUT-'].update(command)
                        except:
                            print('Hm... Something wrong.', end='\n\n>> ')
                self.window.close()
        else:
            self.window.close()
            if self.user == 'user_do_not_input':
                self.print("User wasn't input.")


class VRFileHosting(VRGUI, VRPrint):
    def __init__(self, directory=os.getcwd(), GUI_type=file_hosting, title='VaspReader', theme='VRGUI'):
        super(VRFileHosting, self).__init__(GUI_type, title, resizable=True, keep_on_top=False, return_keyboard_events=True, theme=theme)
        VRPrint.__init__(self)
        self.theme = theme
        self.event, self.value = None, None
        self.folders_local = ['.' * 64] + os.listdir(directory) if directory else ['.' * 64] + os.listdir()
        self.local_tree, self.server_tree = sg.TreeData(), sg.TreeData()
        self.local_tree_focus, self.server_tree_focus = False, False
        self.window['-LOCALTREE-'].bind('<Double-1>', "DOUBLE-CLICK-")
        self.window['-SERVERTREE-'].bind('<Double-1>', "DOUBLE-CLICK-")
        self.window['-LOCALTREE-'].Widget.bind('<Button-3>', lambda event, element=self.window['-LOCALTREE-']: self.RightClickMenuCallback(event, element))
        self.window.TKroot.bind('<B1-Motion>', self.IconMotionCallback)
        self.window.TKroot.bind('<ButtonRelease-1>', self.ButtonReleaseCallback)
        self.window['-LOCALTREE-'].Widget.bind('<Enter>', lambda event, element=self.window['-LOCALTREE-']: self.FocusEvent(event, element))
        self.window['-LOCALTREE-'].Widget.bind('<Leave>', lambda event, element=self.window['-LOCALTREE-']: self.FocusEvent(event, element))
        self.window['-SERVERTREE-'].Widget.bind('<Enter>', lambda event, element=self.window['-SERVERTREE-']: self.FocusEvent(event, element))
        self.window['-SERVERTREE-'].Widget.bind('<Leave>', lambda event, element=self.window['-SERVERTREE-']: self.FocusEvent(event, element))
        self.window['-LOCALTREE-'].Widget.bind('<Button-1>', lambda event, element=self.window['-LOCALTREE-']: self.get_location(event, element))
        self.window['-SERVERTREE-'].bind('<Button-3>', ' SELECT')
        self.now_dir_local, self.now_dir_server, self.parent = directory, '', ''
        self.parent_dir_local, self.parent_dir_server = '', ''
        self.sleepzone, self.sftp, self.ssh, self.user = '', '', '', ''
        self.selected_row, self.last_focus = '', ''
        self.local_tree_moving_frame, self.move_from = '', ''
        self.rename_frame = ''
        self.create_frame = ''
        self.add_treedata_local(directory)
        self.window['-LOCALTREE-'].update(values=self.local_tree)

    def FocusEvent(self, event, element):
        focus = False if 'Leave' in event.__repr__() else True
        self.last_focus = element
        if element == self.window['-LOCALTREE-']:
            self.local_tree_focus = True if focus else False
        elif element == self.window['-SERVERTREE-']:
            self.server_tree_focus = True if focus else False

    def add_elements_to_local_tree(self, dirname, folder_icon, file_icon):
        files = os.listdir(dirname)
        self.local_tree.Insert('', self.parent_dir_local, '...', values=[], icon=r'VR_icons\previous-folder.ico')
        for f in files:
            fullname = dirname + f
            if os.path.isdir(fullname):
                self.local_tree.Insert('', fullname, f, values=[], icon=folder_icon)
            else:
                self.icon_choose_local('', fullname, f, file_icon)

    def add_treedata_local(self, dirname):
        dirname_split = dirname.split('\\')
        self.parent_dir_local = '\\'.join(dirname_split[:-1]) if len(dirname_split) > 1 else dirname
        dirname = f'{dirname}\\'
        if os.path.isdir(dirname):
            folder_icon = r'VR_icons\folder.ico'  # os.path.dirname(os.path.abspath(__file__))
            file_icon = r'VR_icons\file.ico'
            try:
                self.add_elements_to_local_tree(dirname, folder_icon, file_icon)
            except PermissionError:
                self.now_dir_local = self.parent_dir_local
                self.add_treedata_local(self.parent_dir_local)
        else:
            self.add_treedata_local(self.parent_dir_local)

    def add_treedata_server(self, dirname):
        self.parent_dir_server = '/'.join(dirname.split('/')[:-1]) if len(dirname.split('/')) > 1 else dirname
        file_cheak = self.sftp.lstat(dirname)
        perm = oct(file_cheak.st_mode)[:4]
        if perm == '0o40':
            folder_icon = r'VR_icons\folder.ico'
            file_icon = r'VR_icons\file.ico'
            self.server_tree.Insert('', self.parent_dir_server, '...', values=[], icon=folder_icon)
            self.sftp.chdir(dirname)
            files = self.sftp.listdir_attr(dirname)
            for f in files:
                if f.filename.startswith('.'):
                    continue
                else:
                    fullname = dirname + '/' + f.filename
                    if oct(f.st_mode)[:4] == '0o40':
                        self.server_tree.Insert('', fullname, f.filename, values=[], icon=folder_icon)
                    else:
                        self.icon_choose_server('', fullname, f.filename, f.st_size, f.st_mtime, file_icon)
        else:
            self.add_treedata_server(self.parent_dir_server)

    def icon_choose_local(self, parent, fullname, f, file_icon):
        mod_time = datetime.datetime.fromtimestamp(os.stat(fullname).st_mtime).strftime('%H:%M %d-%m-%Y')
        try:
            if fullname.endswith('.rar') or fullname.endswith('.zip'):
                self.local_tree.Insert(parent, fullname, f, values=[bytes_size_convert(os.stat(fullname).st_size), mod_time], icon=r'VR_icons/winrar.ico')
            elif fullname.endswith('.xls') or fullname.endswith('.xlsx') or fullname.endswith('.csv'):
                self.local_tree.Insert(parent, fullname, f, values=[bytes_size_convert(os.stat(fullname).st_size), mod_time], icon=r'VR_icons/excel.ico')
            elif fullname.endswith('.doc') or fullname.endswith('.docx'):
                self.local_tree.Insert(parent, fullname, f, values=[bytes_size_convert(os.stat(fullname).st_size), mod_time], icon=r'VR_icons/doc.ico')
            elif fullname.endswith('.pdf'):
                self.local_tree.Insert(parent, fullname, f, values=[bytes_size_convert(os.stat(fullname).st_size), mod_time], icon=r'VR_icons/pdf.ico')
            elif fullname.endswith('.png') or fullname.endswith('.jpg'):
                self.local_tree.Insert(parent, fullname, f, values=[bytes_size_convert(os.stat(fullname).st_size), mod_time], icon=r'VR_icons/png.ico')
            elif fullname.endswith('.txt'):
                self.local_tree.Insert(parent, fullname, f, values=[bytes_size_convert(os.stat(fullname).st_size), mod_time], icon=r'VR_icons/txt.ico')
            else:
                self.local_tree.Insert(parent, fullname, f, values=[bytes_size_convert(os.stat(fullname).st_size), mod_time], icon=file_icon)
        except FileNotFoundError:
            self.local_tree.Insert(parent, fullname, f, values=[bytes_size_convert(os.stat(fullname).st_size), mod_time], icon=file_icon)

    def icon_choose_server(self, parent, fullname, filename, size, modify_time, file_icon):
        mod_time = datetime.datetime.fromtimestamp(modify_time).strftime('%H:%M %d-%m-%Y')
        try:
            if fullname.endswith('.rar') or fullname.endswith('.zip'):
                self.server_tree.Insert(parent, fullname, filename, values=[bytes_size_convert(size), mod_time], icon=r'VR_icons/winrar.ico')
            elif fullname.endswith('.xls') or fullname.endswith('.xlsx') or fullname.endswith('.csv'):
                self.server_tree.Insert(parent, fullname, filename, values=[bytes_size_convert(size), mod_time], icon=r'VR_icons/excel.ico')
            elif fullname.endswith('.doc') or fullname.endswith('.docx'):
                self.server_tree.Insert(parent, fullname, filename, values=[bytes_size_convert(size), mod_time], icon=r'VR_icons/doc.ico')
            elif fullname.endswith('.pdf'):
                self.server_tree.Insert(parent, fullname, filename, values=[bytes_size_convert(size), mod_time], icon=r'VR_icons/pdf.ico')
            elif fullname.endswith('.png') or fullname.endswith('.jpg') or fullname.endswith('.jpeg'):
                self.server_tree.Insert(parent, fullname, filename, values=[bytes_size_convert(size), mod_time], icon=r'VR_icons/png.ico')
            elif fullname.endswith('.txt'):
                self.server_tree.Insert(parent, fullname, filename, values=[bytes_size_convert(size), mod_time], icon=r'VR_icons/txt.ico')
            else:
                self.server_tree.Insert(parent, fullname, filename, values=[bytes_size_convert(size), mod_time], icon=file_icon)
        except FileNotFoundError:
            self.server_tree.Insert(parent, fullname, filename, values=[bytes_size_convert(size), mod_time], icon=file_icon)

    def get_location(self, event, element):
        widget = element.Widget
        row = None
        region = widget.identify('region', event.x, event.y)
        if region in ('nothing', 'separator', 'heading'):
            row = None
        elif region in ('tree', 'cell'):
            row = widget.identify_row(event.y)
        if row in element.IdToKey:
            row = element.IdToKey[row]
            selection = element.KeyToID[row]
            widget.selection_set(selection)
        else:
            widget.selection_set('')
        if self.rename_frame:
            self.rename_frame.destroy()
            self.rename_frame = ''
        if self.create_frame:
            self.create_frame.destroy()
            self.create_frame = ''

    def IconMotionCallback(self, event):
        if (self.value['-LOCALTREE-'] or self.value['-SERVERTREE-']) and not self.local_tree_moving_frame:
            image = self.window['-LOCALTREE-'].TreeData.tree_dict[self.value['-LOCALTREE-'][0]].icon
            img = Image.open(image)
            img = img.resize((20, 20))
            img = ImageTk.PhotoImage(img)
            text = self.window['-LOCALTREE-'].TreeData.tree_dict[self.value['-LOCALTREE-'][0]].text
            text_variable = sg.tk.StringVar()
            text_variable.set(text)
            self.local_tree_moving_frame = sg.tk.Frame(self.window.TKroot)
            self.local_tree_moving_frame.pack()
            label = sg.tk.Label(self.local_tree_moving_frame, image=img)
            label.image = img
            label.pack(side="left", fill="both", padx=2)
            text_element = sg.tk.Label(self.local_tree_moving_frame, textvariable=text_variable)
            text_element.pack(side='right')
            self.move_from = 'local' if self.value['-LOCALTREE-'] else 'server'
        if self.local_tree_moving_frame:
            if self.local_tree_focus:
                if self.value['-SERVERTREE-']:
                    self.window['-SERVERTREE-'].Widget.selection_set('')
                self.get_location(event, self.window['-LOCALTREE-'])
            elif self.server_tree_focus:
                if self.window['-LOCALTREE-']:
                    self.window['-LOCALTREE-'].Widget.selection_set('')
                self.get_location(event, self.window['-SERVERTREE-'])
            self.local_tree_moving_frame.place(x=event.x, y=event.y, anchor="nw", height=20)

    def ButtonReleaseCallback(self, event):
        if self.local_tree_moving_frame:
            file = list(self.local_tree_moving_frame.children.values())[-1].cget("text")
            file_path = f'{self.now_dir_local}\\{file}'
            if self.value['-LOCALTREE-']:
                to_path = self.value['-LOCALTREE-'][0]
            elif self.value['-SERVERTREE-']:
                to_path = self.value['-SERVERTREE-'][0]
            else:
                to_path = None
            if self.value['-LOCALTREE-'] and self.move_from == 'local' and file_path != to_path:
                try:
                    if os.path.isdir(to_path):
                        os.replace(file_path, f'{to_path}\\{file}')
                        self.local_tree_refresh()
                except PermissionError:
                    self.print('You have no enough permissions to do this.')
            self.local_tree_moving_frame.destroy()
            self.local_tree_moving_frame = ''

    def RightClickMenuCallback(self, event, element):
        widget = element.Widget
        row = None
        region = widget.identify('region', event.x, event.y)
        if region in ('nothing', 'separator', 'heading'):
            row = None
        elif region in ('tree', 'cell'):
            row = widget.identify_row(event.y)
        if row in element.IdToKey and element.IdToKey[row] != self.parent_dir_local:
            row = element.IdToKey[row]
            selection = element.KeyToID[row]
            widget.selection_set(selection)
            element.TKRightClickMenu.tk_popup(event.x_root, event.y_root, 0)
            element.TKRightClickMenu.grab_release()
        else:
            widget.selection_set('')

    @ staticmethod
    def check_permissions(path):
        bytes_string = bin(os.lstat(path).st_mode)[-9:]
        permissions_list = tuple(map(lambda x: bool(int(x)), list(bytes_string)))[:2]
        num_mode = [ind + 1 for ind, val in enumerate(permissions_list) if val]
        modes = ['n', 'r', 'w', 'r+w']
        return modes[sum(num_mode)]

    def rename_callback(self, event, text, filepath, key):
        widget = event.widget
        text = filepath
        if key == 'Return':
            text = self.now_dir_local + '\\' + widget.get()
            try:
                os.rename(filepath, text)
                self.local_tree_refresh()
            except PermissionError:
                self.print('You don\' have enough permissions to complete this operation.')
        widget.destroy()
        widget.master.destroy()

    def rename_event(self, element):
        table = self.window[element].Widget
        root = table.master
        x, y, width, height = table.bbox(self.window[element].KeyToID[self.value[element][0]], '#0')

        image = self.window[element].TreeData.tree_dict[self.value[element][0]].icon
        img = Image.open(image)
        img = img.resize((20, 20))
        img = ImageTk.PhotoImage(img)
        text = self.window[element].TreeData.tree_dict[self.value[element][0]].text
        text_variable = sg.tk.StringVar()
        text_variable.set(text)
        self.rename_frame = sg.tk.Frame(root)
        self.rename_frame.pack()
        label = sg.tk.Label(self.rename_frame, image=img)
        label.image = img
        label.pack(side="left", fill="both", padx=(15, 0))
        entry_element = sg.tk.Entry(self.rename_frame, textvariable=text_variable, width=width-17)
        entry_element.pack(side='left', padx=(0, 2), fill='both')
        entry_element.select_range(0, sg.tk.END)
        entry_element.icursor(sg.tk.END)
        entry_element.focus_force()
        entry_element.bind("<Return>", lambda event, text=text, filepath=self.value[element][0], key='Return': self.rename_callback(event, text, filepath, key))
        entry_element.bind("<Escape>", lambda event, text=text, filepath=self.value[element][0], key='Escape': self.rename_callback(event, text, filepath, key))
        self.rename_frame.place(x=x, y=y, anchor="nw", width=width, height=height)

    def local_tree_refresh(self):
        self.local_tree = sg.TreeData()
        self.add_treedata_local(self.now_dir_local)
        self.window['-LOCALTREE-'].update(values=self.local_tree)

    def delete_file(self):
        if self.value['-LOCALTREE-'] or self.value['-SERVERTREE-']:
            event, value = VRGUI(GUI_type=ask_to_delete_file, title='VaspReader', theme=self.theme, keep_on_top=True, return_keyboard_events=True).window_return().read(close=True)
            if event == '-YES-' or event == '\r':
                to_delete = self.value['-LOCALTREE-'][0] if self.value['-LOCALTREE-'] else self.value['-SERVERTREE-']
                try:
                    os.rmdir(to_delete) if os.path.isdir(to_delete) else os.remove(to_delete)
                    self.local_tree_refresh()
                except PermissionError:
                    self.print('You don\'t have enough permissions to do this.')

    def create_file_or_folder(self, element, create):
        table = self.window[element].Widget
        root = table.master
        x, y, width, height = table.bbox(self.window[element].KeyToID[list(self.window[element].TreeData.tree_dict.keys())[-1]], '#0')
        img = Image.open(r'VR_icons\folder.ico' if type == 'folder' else r'VR_icons\file.ico')
        img = img.resize((20, 20))
        img = ImageTk.PhotoImage(img)
        text_variable = sg.tk.StringVar()
        self.create_frame = sg.tk.Frame(root)
        self.create_frame.pack()
        label = sg.tk.Label(self.create_frame, image=img)
        label.image = img
        label.pack(side="left", fill="both", padx=(15, 0))
        entry_element = sg.tk.Entry(self.create_frame, textvariable=text_variable, width=width - 17)
        entry_element.pack(side='left', padx=(0, 2), fill='both')
        entry_element.select_range(0, sg.tk.END)
        entry_element.icursor(sg.tk.END)
        entry_element.focus_force()
        entry_element.bind("<Return>", lambda event, key='Return', create=create: self.create_folder_callback(event, key, create))
        entry_element.bind("<Escape>", lambda event, key='Escape', create=create: self.create_folder_callback(event, key, create))
        self.create_frame.place(x=x, y=y + 16, anchor="nw", width=width, height=height)

    def create_folder_callback(self, event, key, create):
        widget = event.widget
        if key == 'Return':
            try:
                if create == 'folder':
                    os.mkdir(f'{self.now_dir_local}\\{widget.get()}')
                elif create == 'file':
                    file = open(f'{self.now_dir_local}\\{widget.get()}', 'x')
                    file.close()
                self.local_tree_refresh()
            except PermissionError:
                self.print('You don\'t have enough permissions to do this.')
            except FileExistsError:
                self.print('Such folder already exist.')
        widget.destroy()
        self.create_frame.destroy()
        self.create_frame = ''

    def connect_to_server(self):
        self.user = _authentication()
        if self.user not in ['break', 'user_do_not_input']:
            self.ssh = paramiko.SSHClient()
            self.window.perform_long_operation(lambda: self.connecting(), '-STABLECONNECT-')

    def connecting(self):
        self.now_dir_server, self.sleepzone, self.sftp = '', '', ''
        try:
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect('lomonosov2.parallel.ru', username=self.user)
            self.sftp = self.ssh.open_sftp()
            self.now_dir_server = self.sftp.normalize('.')
            self.sleepzone = '/'.join(self.now_dir_server.split('/')[:-1]) if len(self.now_dir_server.split('/')) > 1 else self.now_dir_server
            self.server_tree_refresh()
        except socket.error as exc:
            self.print('Caught exception socket.error : %s' % exc)
        except paramiko.ssh_exception.AuthenticationException:
            self.print('No such user. Try to connect again.')
        except paramiko.ssh_exception.SSHException:
            self.print('No authentication methods available. Add ssh key to Pegeant to work with console.')
        # except OSError:
        #     pass
        except Exception as exc:
            self.print('Exception: ' + traceback.format_exc() + ' has been occured.')
        return self.now_dir_server, self.sleepzone, self.sftp

    def server_tree_refresh(self):
        self.server_tree = sg.TreeData()
        self.add_treedata_server(self.now_dir_server)
        self.window['-SERVERTREE-'].update(values=self.server_tree)

    def mainloop(self):
        while True:
            self.event, self.value = self.window.read()
            if self.event == sg.WIN_CLOSED:
                self.window.close()
                _close_ssh(self.sftp)
                _close_ssh(self.ssh)
                break
            if self.event == 'Rename':
                self.rename_event('-LOCALTREE-')
            if self.event == 'File':
                self.create_file_or_folder('-LOCALTREE-', 'file')
            if self.event == 'Folder':
                self.create_file_or_folder('-LOCALTREE-', 'folder')
            if self.event == '-LOCALTREE-DOUBLE-CLICK-' or self.event == 'Open' or self.event == '\r':
                try:
                    permissions = self.check_permissions(self.value['-LOCALTREE-'][0])
                    if permissions != 'n':
                        if not os.path.isdir(self.value['-LOCALTREE-'][0]):
                            file_dir = self.value['-LOCALTREE-'][0].lower()
                            if file_dir.endswith('.exe') or file_dir.endswith('.pptx') or file_dir.endswith('.ppt') or file_dir.endswith('.zip') or file_dir.endswith('.rar') or file_dir.endswith('.url') or file_dir.endswith('.png') or file_dir.endswith('.pdf') or file_dir.endswith('.ico') or file_dir.endswith('.jpg') or file_dir.endswith('.jpeg') or file_dir.endswith('.doc') or file_dir.endswith('.docx') or file_dir.endswith('.xls') or file_dir.endswith('.xlsx') or file_dir.endswith('.tif') or file_dir.endswith('.tiff'):
                                os.startfile(self.value['-LOCALTREE-'][0])
                            else:
                                VRRedactor(open_directory=self.value['-LOCALTREE-'][0]).mainloop()
                        self.now_dir_local = self.value['-LOCALTREE-'][0] if os.path.isdir(self.value['-LOCALTREE-'][0]) else self.now_dir_local
                        self.local_tree_refresh()
                except IndexError:
                    pass
            if self.event == '-CHNGDIR-':
                file_path = sg.PopupGetFolder(message='Change folder', no_window=True, no_titlebar=True, icon=self.icon_image)
                if file_path:
                    self.now_dir_local = '\\'.join(file_path.split('/'))
                    self.local_tree_refresh()
            if self.event == '-REFRESHDIR-':
                self.local_tree_refresh()
            if self.event == 'Delete':
                self.delete_file()
            if self.event == '-CONNECT-':
                self.connect_to_server()
            if self.event == '-STABLECONNECT-':
                self.now_dir_server, self.sleepzone, self.sftp = self.value['-STABLECONNECT-']
            # if self.event == '-LOCALTREE- SELECT':
            #     row = self.get_location(self.window['-LOCALTREE-'], self.window['-LOCALTREE-'].user_bind_event)
            #     if row is not None and row != self.parent_dir_local:
            #         selection = self.window['-LOCALTREE-'].KeyToID[row]
            #         self.window['-LOCALTREE-'].widget.selection_set(selection)
            #         self.window['-LOCALTREE-'].TKRightClickMenu.tk_popup(self.window['-LOCALTREE-'].user_bind_event.x_root, self.window['-LOCALTREE-'].user_bind_event.y_root, 0)
            #         self.window['-LOCALTREE-'].TKRightClickMenu.grab_release()


# VRFileHosting().mainloop()
