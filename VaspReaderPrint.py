import datetime
import time
from functools import lru_cache
import base64
from PIL import Image
import io
import PySimpleGUI as sg
import codecs
from functools import partial
import os
import ast


class Print:
    sg.LOOK_AND_FEEL_TABLE['VRPrint'] = {'BACKGROUND': 'Black', 'TEXT': '#3a005e', 'INPUT': 'Black', 'TEXT_INPUT': 'turquoise', 'SCROLL': '#3a005e',
                                         'BUTTON': ('Black', '#3a005e'), 'PROGRESS': ('#D1826B', '#CC8019'), 'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0, }

    def __init__(self, background_image=None, grab_anywhere=True):
        sg.theme('VRPrint')
        self.text_color, self.background_color, self.font = None, None, ('Times', 9)
        self.background, self.background_exist = None, True
        if background_image is not None:
            try:
                in_mem_file = io.BytesIO()
                self.window = sg.Window(title='VaspReader', layout=self.Print_GUI(), resizable=False, alpha_channel=0.8, relative_location=(-440, -220), grab_anywhere=grab_anywhere, keep_on_top=False, finalize=True)
                img = Image.open(background_image).resize(self.window.size)
                img.save(in_mem_file, format="PNG")
                in_mem_file.seek(0)
                img = in_mem_file.read()
                img = base64.b64encode(img).decode('ascii')
                self.background = sg.Window('', layout=[[sg.Image(data=img)]], size=self.window.size, no_titlebar=True, finalize=True, margins=(0, 0), element_padding=(0, 0))
                position = self.window.CurrentLocation()
                self.background.move(*position)
                self.window.bring_to_front()
                self.window.TKroot.bind('<Configure>', lambda event: self.move_function(event))
                self.window.TKroot.bind('<Map>', lambda event: self.map_function(event))
                self.window.TKroot.bind('<Unmap>', lambda event: self.unmap_function(event))
                self.window.TKroot.bind('<Destroy>', lambda event: self.destroy_function(event))
                self.window.TKroot.bind('<FocusIn>', lambda event: self.focus_in_function(event))
            except:
                self.window.close()
                self.window = sg.Window(title='VaspReader', layout=self.Print_GUI(), resizable=False, relative_location=(-440, -220), grab_anywhere=True, keep_on_top=False, finalize=True)
                self.background_exist = False
        else:
            self.window = sg.Window(title='VaspReader', layout=self.Print_GUI(), resizable=False, relative_location=(-440, -220), grab_anywhere=True, keep_on_top=False, finalize=True)
            self.background_exist = False
        return

    def focus_in_function(self, event):
        self.background.bring_to_front()
        self.window.bring_to_front()

    def destroy_function(self, event):
        if self.background is not None:
            self.background.close()
            self.background = None

    def map_function(self, event):
        self.background.un_hide()
        self.window.bring_to_front()

    def unmap_function(self, event):
        self.background.hide()

    def move_function(self, event):
        self.background.move(event.x + 8, event.y + 30)

    @ staticmethod
    def Print_GUI():
        layout = [[sg.Multiline(autoscroll=True, auto_refresh=True, disabled=True, key='-PRINT-', size=(60, 16), expand_x=True, expand_y=True, pad=((0, 0), (0, 0)))]]
        return layout

    def reopen_window(self):
        if self.window is None or (self.window is not None and self.window.was_closed()):
            self.__init__()

    def print(self, *args, end=None, sep=None, text_color='', background_color='', font=()):
        text_color = text_color if text_color else self.text_color
        background_color = background_color if background_color else self.background_color
        font = font if font else self.font
        self.reopen_window()
        end_str = str(end) if end is not None else '\n'
        sep_str = str(sep) if sep is not None else ' '

        outstring = ''
        num_args = len(args)
        for i, arg in enumerate(args):
            outstring += str(arg)
            if i != num_args - 1:
                outstring += sep_str
        outstring += end_str
        try:
            self.window['-PRINT-'].update(outstring, append=True, text_color_for_value=text_color, background_color_for_value=background_color, font_for_value=font)
        except:
            self.window = None
            self.reopen_window()
            self.window['-PRINT-'].update(outstring, append=True, text_color_for_value=text_color, background_color_for_value=background_color, font_for_value=font)

    def close(self):
        self.window.close()
        if self.background is not None and self.background_exist:
            self.background.close()
            self.background = None
        self.window = None


class VRPrint:
    now = datetime.datetime.now()
    time_parameters = (now.hour, now.minute, now.second, now.day, now.month, now.year)
    start_string = "VaspReader for Windows 10 (64-bit), \N{Copyright Sign} ver. 2.0.0 (created: 20.02.2022, " \
                   "lat.ver. 30.08.2022)\nEmail questions, suggestions and bug reports to: " \
                   "solovykh.aa19@physics.msu.ru\n---Current time: {0:02}:{1:02}:{2:02}; " \
                   "Date: {3:02}.{4:02}.{5:04}---\n"
    print_window = Print(background_image=r'Debug_Wallpaper\belka.jpg')

    def __init__(self):
        try:
            icon_image = r'VR_icons/VR-logo.ico'
            sg.set_global_icon(icon_image)
        except:
            icon_image = None
        self.print = self.print_window.print
        self.popup = partial(sg.popup, auto_close=True, auto_close_duration=3, keep_on_top=True)

    def start_program(self):
        self.print(self.start_string.format(*self.time_parameters))

    def about_the_program(self):
        self.print('VaspReader is a program firstly for processing and visualizing the results of VASP calculations Have additional modes for simplify your life as more as it possible. '
                   'It was developed at the end of 2021 and has undergone many changes described in other features of the help menu.')

    def latest_update(self):
        self.print("\u262D ver. 3.0.0: \u262D\n"
                   "\u2705 Global update:\n"
                   "1. VaspReader, consisting of several windows, has been redesigned into one main window with a settings menu before processing. It consists of many useful features such as: parsing calculation, configuration state loading/saving, loading/saving from/to json parsed calculations and others. You can find the entire list of options using the change history option.\n"                   
                   "2. The position of the main window is now saved when the window is closed and after starting the program it will be in the saved position.\n"
                   "3. Created two window themes: white and black. The theme is also saved when the window is closed.\n"
                   "4. Added two functions: view model cell and axes.\n"
                   "5. The position of the light can now be set by 8 edges of the cube.\n"
                   "6. Added a convenient option to change the background.\n"
                   "7. In the latest version, an orthogonal view of the model with the mode of selecting atoms has been added.\n"
                   "8. NEW PERFECT FEATURE: The camera can be moved in all directions. You can find the binding keys in the visual description of the window.\n"
                   "9. The bonds calculation function now activates the bonds editing window with 3 modes: all bonds, selected bonds and the drawing trajectory tab. A description of these options can be found in the update history.\n"
                   "10. Reworked windows OSZICAR, POSCAR. The new graphical interface for these windows allows, for example, checking curves from an OSZICAR file or drawing POSCAR/CONTCAR files in the visual window.")

    def updates_history(self):
        with codecs.open('PreviousChanges.txt', 'r', encoding='utf-8') as previous_file:
            self.print(previous_file.read())

    def visual_window_description(self):
        description = 'Main VaspReader windows consists of control panel with the ability to add and delete ' \
                      'calculations, processing them and use some additional modes such as work with supercomputer, ' \
                      'parsing OSZICAR files, reading and work with POSCAR files and some others functions and ' \
                      'visualizing of calculations window with changeable settings, such as lightning, background ' \
                      'color, bounds draw and some others functions. Key assignments: +, - on keypad or keyboard or ' \
                      'mouse scroll to zoom, a - to add an atom to the list, d - to remove an atom from the list, ' \
                      'z - to move camera left, x - right, u - up, j - down, ' \
                      'Backspace - return model to the first position, use arrows to rotate the model.'
        self.print(description, text_color='Brown')

    def file_not_found_message(self, file_name, directory, additional_check=''):
        try:
            self.print(f'You entered: {directory}')
            catcher = os.listdir(directory)
            if additional_check:
                ast.literal_eval(additional_check)
        except FileNotFoundError or OSError or NameError:
            self.print("No such directory! Try again!")
            return True
        except ValueError:
            self.print(f"{file_name} file not found in this directory! Try again!")
            return True
        else:
            return False
