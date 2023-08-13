import PySimpleGUI as sg


#  Main window GUI
def core_GUI():
    menu_def = [['&File', ['&Open Calculation     Ctrl-O', '---', '&Save Calc State       Ctrl-S', '&Load Calc State       Ctrl-L', '---', 'Save Program Configuration', 'Load Program Configuration', '---', 'Send to tray', 'E&xit']],
                ['&Edit', ['View axes', 'View cell boarder', 'Del coords after leave a cell', 'Light', ['Light1', 'Light2', 'Light3', 'Light4', 'Light5', 'Light6', 'Light7', 'Light8'], 'Visualization Type', ['Perspective', 'Orthographic'], 'Background Color']],
                ['&Mods', ['Processing', 'Spectrum', 'Supercomputer', ['Console', 'File hosting'], 'OSZICAR', 'POSCAR', 'CHGCAR', 'Graphs']],
                ['&Tools', ['Select mode', ['Keyboard', 'Mouse+Keyboard', 'Select from listbox'], '---', 'Calculate bonds', 'Set/Unset', ['ID', 'Bond length', 'Valence angle'], '---', 'Form POSCAR', '---', 'Screenshot']],
                ['&Help', ['&About the program', 'Window description', 'Latest update', 'Changes history']]]
    s_m = {'range': (0, 0), 'resolution': 1, 'default_value': 0, 'size': (26, 15), 'orientation': 'horizontal', 'font': ('Arial Black', 5), 'enable_events': True}
    s_vis = {'range': (1, 100), 'resolution': 1, 'default_value': 30, 'size': (27, 15), 'orientation': 'horizontal', 'font': ('Arial Black', 5), 'enable_events': True}
    layout = [[sg.Menu(menu_def, pad=(0, 0), key='-MENUBAR-')],
              [sg.InputText('', size=(34, 1), expand_x=True, key='-DIRECTORY-', enable_events=True, pad=((1, 5), (10, 0))),
               sg.FolderBrowse('Browse', pad=((5, 4), (0, 0)), font=('', 8)),
               sg.Button('Add', enable_events=True, key='-MD-', pad=((1, 1), (0, 0)), font=('', 8))],
              [sg.Combo(values=[], expand_x=True, enable_events=True, key='-MDCALC-', readonly=True, pad=((1, 5), (0, 0))),
               sg.Button('Delete', enable_events=True, key='-MDDEL-', size=(12, 1), pad=((5, 1), (0, 0)), font=('', 8))],
              [sg.Listbox(values=[], select_mode='multiple', key='selected_atoms', enable_events=True, size=(25, 5), expand_x=True, expand_y=True, pad=((1, 1), (0, 0)), visible=False)],
              [sg.Input(key='-BACCOL-', visible=False, enable_events=True),
               sg.ColorChooserButton('', visible=False, key='-BUTCOL-')],
              [sg.Button('\u261A', key='-CALCSTART-', border_width=1, size=(2, 1), pad=((1, 1), (1, 1)), font=('TimesNewRoman', 10)),
               sg.Button('\u25C0', key='-CALCTOSTART-', border_width=1, size=(2, 1), pad=((1, 1), (1, 1)), font=('TimesNewRoman', 10)),
               sg.Slider(**s_m, key='slider', expand_x=True, relief=sg.RELIEF_SUNKEN, pad=((1, 1), (1, 1))),
               sg.Button('\u25B6', key='-CALCTOEND-', border_width=1, size=(2, 1), pad=((1, 1), (1, 1)), font=('TimesNewRoman', 10)),
               sg.Button('\u261B', key='-CALCEND-', border_width=1, size=(2, 1), pad=((1, 1), (1, 1)), font=('TimesNewRoman', 10))],
              [sg.Button('\u263D', key='-THEMECHANGE-', border_width=1, size=(2, 1), pad=((1, 1), (1, 1)), font=('TimesNewRoman', 10)),
               sg.Slider(**s_vis, key='slider_speed', expand_x=True, relief=sg.RELIEF_SUNKEN, pad=((1, 1), (1, 1))),
               sg.Button('Exit', tooltip="Press", key='-EXIT-', border_width=2, size=(10, 1), pad=((1, 1), (1, 1)))]]
    return layout


#  Processing window GUI
def processing_GUI():
    Distanse_sg = [[sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                   [sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
                    sg.Column(
                        [[sg.Listbox([], enable_events=True, key='DistAtoms', select_mode='multiple', size=(15, 5))],
                         [sg.InputText('', key='DistList', readonly=True, text_color='green', size=(17, 1))]],
                        size=(150, 130)),
                    sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
                    sg.Column([[sg.Button('Add column', tooltip="Press", border_width=2, key='AddDist',
                                          size=(14, 1), disabled=True)]], justification='left'),
                    sg.VerticalSeparator(color='gray', pad=((2, 0), (0, 0)))],
                   [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                   [sg.VerticalSeparator(color='gray', pad=((0, 5), (0, 0))),
                    sg.Combo([], enable_events=True, key='DistAdded', readonly=True, disabled=True, size=(17, 1)),
                    sg.VerticalSeparator(color='gray', pad=((9, 5), (0, 0))),
                    sg.Button('Remove Column', size=(14, 1), key='RemoveDist', disabled=True, tooltip="Press",
                              border_width=2),
                    sg.VerticalSeparator(color='gray', pad=((7, 0), (0, 0)))],
                   [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))]]
    Distanse_sg_tab = sg.Tab(title='Distance', layout=Distanse_sg)
    Angle_sg = [[sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                [sg.VerticalSeparator(color='gray', pad=((0, 5), (0, 0))),
                 sg.Column([[sg.Listbox([], enable_events=True, key='AtomAngle', select_mode='multiple', size=(15, 5))],
                            [sg.InputText('', key='AtomList', readonly=True, text_color='green', size=(17, 1))]], pad=((2, 0), (0, 5))),
                 sg.VerticalSeparator(color='gray', pad=((5, 5), (0, 0))),
                 sg.Column([[sg.Button('Add Column', size=(12, 1), key='AddAngle', tooltip="Press", border_width=2, disabled=True, expand_x=True)],
                            [sg.Checkbox('xy', default=False, enable_events=True, key='xy', disabled=True, pad=((4, 0), (5, 0))),
                             sg.Checkbox('yz', default=False, enable_events=True, key='yz', disabled=True, pad=((5, 0), (5, 0))),
                             sg.Checkbox('zx', default=False, enable_events=True, key='zx', disabled=True, pad=((5, 4), (5, 0)))]],
                           pad=((0, 0), (44, 27)), justification='center'),
                 sg.VerticalSeparator(color='gray', pad=((5, 0), (0, 0)))],
                [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                [sg.VerticalSeparator(color='gray', pad=((0, 5), (0, 0))),
                 sg.Combo([], enable_events=True, key='AngleAdded', readonly=True, disabled=True, size=(17, 1)),
                 sg.VerticalSeparator(color='gray', pad=((9, 5), (0, 0))),
                 sg.Button('Remove Column', size=(14, 1), key='RemoveAngle', disabled=True, tooltip="Press", border_width=2),
                 sg.VerticalSeparator(color='gray', pad=((7, 0), (0, 0)))],
                [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))]]
    Angle_sg_tab = sg.Tab(title='Angle', layout=Angle_sg)
    weightmass_sg = [[sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                     [sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
                      sg.Column([[sg.Listbox([], enable_events=True, key='WeightAtom', select_mode='multiple', size=(15, 5))],
                                 [sg.InputText('', key='WeightList', readonly=True, text_color='green', size=(17, 1))]], size=(150, 130)),
                      sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
                      sg.Column([[sg.Button('Add COM', tooltip="Press", border_width=2, key='AddAtomWeight', size=(14, 1), disabled=True)]], justification='left'),
                      sg.VerticalSeparator(color='gray', pad=((2, 0), (0, 0)))],
                     [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                     [sg.VerticalSeparator(color='gray', pad=((0, 5), (0, 0))),
                      sg.Combo([], enable_events=True, key='COMAdded', readonly=True, disabled=True, size=(17, 1)),
                      sg.VerticalSeparator(color='gray', pad=((9, 5), (0, 0))),
                      sg.Button('Remove Column', size=(14, 1), key='RemoveAtomWeight', disabled=True, tooltip="Press", border_width=2),
                      sg.VerticalSeparator(color='gray', pad=((7, 0), (0, 0)))],
                     [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))]]
    weightmass_sg_tab = sg.Tab('COM', weightmass_sg)
    sum_sg = [[sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
              [sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
               sg.Column([[sg.Listbox([], enable_events=True, key='SumAtom', select_mode='multiple', size=(15, 5))],
                          [sg.InputText('', key='SumList', readonly=True, text_color='green', size=(17, 1))]], size=(150, 130)),
               sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
               sg.Column([[sg.Button('Add sum', tooltip="Press", border_width=2, key='AddAtomSum', size=(14, 1), disabled=True)]], justification='left'),
               sg.VerticalSeparator(color='gray', pad=((2, 0), (0, 0)))],
              [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
              [sg.VerticalSeparator(color='gray', pad=((0, 5), (0, 0))),
               sg.Combo([], enable_events=True, key='SumAdded', readonly=True, disabled=True, size=(17, 1)),
               sg.VerticalSeparator(color='gray', pad=((9, 5), (0, 0))),
               sg.Button('Remove Column', size=(14, 1), key='RemoveAtomSum', disabled=True, tooltip="Press", border_width=2),
               sg.VerticalSeparator(color='gray', pad=((7, 0), (0, 0)))],
              [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))]]
    sum_sg_tab = sg.Tab('+', sum_sg)
    minus_sg = [[sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                [sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
                 sg.Column([[sg.Listbox([], enable_events=True, key='MinusAtom', select_mode='multiple', size=(15, 5))],
                            [sg.InputText('', key='MinusList', readonly=True, text_color='green', size=(17, 1))]],
                           size=(150, 130)),
                 sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
                 sg.Column([[sg.Button('Add sum', tooltip="Press", border_width=2, key='AddAtomMinus', size=(14, 1),
                                       disabled=True)]], justification='left'),
                 sg.VerticalSeparator(color='gray', pad=((2, 0), (0, 0)))],
                [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                [sg.VerticalSeparator(color='gray', pad=((0, 5), (0, 0))),
                 sg.Combo([], enable_events=True, key='MinusAdded', readonly=True, disabled=True, size=(17, 1)),
                 sg.VerticalSeparator(color='gray', pad=((9, 5), (0, 0))),
                 sg.Button('Remove Column', size=(14, 1), key='RemoveAtomMinus', disabled=True, tooltip="Press",
                           border_width=2),
                 sg.VerticalSeparator(color='gray', pad=((7, 0), (0, 0)))],
                [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))]]
    minus_sg_tab = sg.Tab('-', minus_sg)
    devide_sg = [[sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                     [sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
                      sg.Column(
                          [[sg.Listbox([], enable_events=True, key='DivideAtoms', select_mode='multiple', size=(15, 5))],
                           [sg.InputText('', key='DivideList', readonly=True, text_color='green', size=(17, 1))]],
                          size=(150, 130)),
                      sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
                      sg.Column([[sg.Button('Add column', tooltip="Press", border_width=2, key='AddAtomsDivide',
                                            size=(14, 1), disabled=True)]], justification='left'),
                      sg.VerticalSeparator(color='gray', pad=((2, 0), (0, 0)))],
                     [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                     [sg.VerticalSeparator(color='gray', pad=((0, 5), (0, 0))),
                      sg.Combo([], enable_events=True, key='DivideAdded', readonly=True, disabled=True, size=(17, 1)),
                      sg.VerticalSeparator(color='gray', pad=((9, 5), (0, 0))),
                      sg.Button('Remove Column', size=(14, 1), key='RemoveAtomsDivide', disabled=True, tooltip="Press",
                                border_width=2),
                      sg.VerticalSeparator(color='gray', pad=((7, 0), (0, 0)))],
                     [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))]]
    divide_sg_tab = sg.Tab('Divide', devide_sg)
    rename_sg = [[sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                 [sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0))),
                  sg.Column([[sg.Combo(values=[], readonly=True, key='RenameColChoose', enable_events=True, expand_x=True, pad=((5, 5), (5, 5)))],
                             [sg.InputText(disabled=True, key='RenameInput', enable_events=True, expand_x=True, pad=((5, 5), (5, 5)))],
                             [sg.Button('Submit', disabled=True, expand_x=True, enable_events=True, key='RenameSubmit')],
                             [sg.Image('VR_icons\\VR-logo.png', expand_y=True, subsample=10, enable_events=True, key='RenameImage')]], element_justification='center', expand_x=True, expand_y=True),
                  sg.VerticalSeparator(color='gray', pad=((0, 0), (0, 0)))],
                 [sg.HorizontalSeparator(color='gray', pad=((0, 0), (0, 0)))]]
    rename_sg_tab = sg.Tab('Rename', rename_sg)
    calc_tab = sg.TabGroup([[Distanse_sg_tab, Angle_sg_tab, weightmass_sg_tab, sum_sg_tab, minus_sg_tab, divide_sg_tab, rename_sg_tab]], size=(310, 176), tab_border_width=2, font=('Times', 10)) # DarkAmber - selected_title_color='green', selected_background_color='gray', tab_background_color='black'
    layout = [[sg.Column([[sg.Text('Window of calculate.')],
                          [sg.Text('Selected atoms: ', size=(16, 1)), sg.InputText('', key='SelectedAtoms', readonly=True, text_color='green', expand_x=True)]]),
               sg.Column([[sg.Checkbox('Include OSZICAR files to the DataFrame', default=False, key='OSZICARcheck', enable_events=True, pad=((5, 5), (1, 1)), disabled=True)],
                          [sg.Checkbox('Activate preview of excel table', default=True, key='TableActiveCheck', enable_events=True, pad=((5, 5), (1, 1)))]])],
              [sg.Column([[sg.Frame(title='Options', layout=[[sg.Checkbox('Delete coordinates of selected atoms.', default=True, key='DelCoordCheck', enable_events=True)],
                                                             [sg.Checkbox('Do not add the energy of the selected atoms.', default=False, key='EnergyCheck', enable_events=True)]],
                                    element_justification='left')],
                          [calc_tab],
                          [sg.Button('Build Graphs', size=(20, 1), tooltip='Press', border_width=2, key='GraphMode', expand_x=True)]], element_justification='left', size=(320, 400)), # , pad=((75, 75), (5, 5)))
               sg.Multiline('', disabled=True, rstrip=False, horizontal_scroll=True, size=(80, 24), key='TablePreview', font=('Consolas', 10), expand_x=True, expand_y=True)],
              [sg.Button('Create Excel file', tooltip="Press", border_width=2, size=(20, 1), key='CreateExcel'),
               sg.Button('Back', tooltip="Back to main window.", border_width=2, size=(10, 1), key='Exit')]]
    # sg.Table() sg.Table(values=[[]], headings=[], justification='center', vertical_scroll_only=False, size=(80, 24), key='TablePreview', expand_x=True, expand_y=True)
    return layout


def graph_processing_GUI():
    """"VaspReader window of creating and saving graphs."""
    graph_interval = [[sg.Text('Set the interval along the axes.')],
                      [sg.Text('X-axis:', pad=((5, 5), (0, 0)))],
                      [sg.Text('from ', size=(5, 1)),
                       sg.InputText(key='fromX', disabled=True, expand_x=True, pad=((5, 9), (0, 0)))],
                      [sg.Text('to ', size=(5, 1)),
                       sg.InputText(key='toX', disabled=True, expand_x=True, pad=((5, 9), (0, 0)))],
                      [sg.Button('Set x limits', expand_x=True, enable_events=True, key='Xlim', disabled=True, pad=((5, 8), (0, 0)), font=('Times', 9))],
                      [sg.Text('Y-axis:', pad=((5, 5), (0, 0)))],
                      [sg.Text('from ', size=(5, 1)),
                       sg.InputText(key='fromY', expand_x=True, disabled=True, pad=((5, 9), (0, 0)))],
                      [sg.Text('to ', size=(5, 1)),
                       sg.InputText(key='toY', expand_x=True, disabled=True, pad=((5, 9), (0, 0)))],
                      [sg.Button('Set y limits', expand_x=True, enable_events=True, key='Ylim', disabled=True, pad=((5, 8), (0, 0)), font=('Times', 9))],
                      [sg.VPush()],
                      [sg.Button('Reset options', expand_x=True, enable_events=True, key='Reset', disabled=True, pad=((5, 8), (0, 5)), font=('Times', 9))]]
    graph_label = [[sg.Text('Input x-axis name: ')],
                   [sg.InputText('Time, fs', key='X-axisName', expand_x=True, pad=((5, 9), (0, 0)), disabled=True)],
                   [sg.Text('Input y-axis name: ')],
                   [sg.InputText('', key='Y-axisName', expand_x=True, pad=((5, 9), (0, 0)), disabled=True)],
                   [sg.VPush()],
                   [sg.Button('Submit', enable_events=True, key='LALS', border_width=2, expand_x=True, pad=((5, 8), (0, 5)), font=('Times', 9))]]
    graph_legend = [[sg.Checkbox('Include graph legend', default=True, enable_events=True, key='LegendIncl', pad=((5, 8), (5, 0)))],
                    [sg.Text('Rename legend: ')],
                    [sg.Combo(values=[], enable_events=True, disabled=True, key='RenameLegend', readonly=True, expand_x=True, pad=((5, 8), (0, 0)))],
                    [sg.Text('Suggesting variants: ')],
                    [sg.Combo(values=[], enable_events=True, disabled=True, key='AutoRename', readonly=True, expand_x=True, pad=((5, 8), (0, 0)))],
                    [sg.InputText('', key='LegendName', expand_x=True, pad=((5, 9), (5, 0)), disabled=True)],
                    [sg.VPush()],
                    [sg.Button('Submit', enable_events=True, key='LApply', border_width=2, disabled=True, expand_x=True, pad=((5, 8), (0, 5)), font=('Times', 9))]]
    graph_width_and_color = [[sg.Text('Choose curve to change: ')],
                             [sg.Combo(values=[], enable_events=True, disabled=True, key='CurveChoose', readonly=True, expand_x=True, pad=((5, 8), (0, 0)))],
                             [sg.Text('Line width: ')],
                             [sg.InputText(disabled=True, key='LineWidth', expand_x=True, enable_events=True, pad=((5, 9), (0, 5)))],
                             [sg.Text('Curve color: ')],
                             [sg.Button('', expand_x=True, disabled=True, key='cur_col', button_color='white', pad=((5, 0), (5, 5)), font=('Times', 9)),
                              sg.ColorChooserButton('Add Color', key='ChCurCol', disabled=True, target='CurCol', pad=((0, 8), (5, 5)), font=('Times', 9)),
                              sg.InputText(disabled=False, key='CurCol', visible=False, enable_events=True)],
                             [sg.VPush()],
                             [sg.Button('Submit', enable_events=True, key='ColorApply', border_width=2, disabled=True, expand_x=True, pad=((5, 8), (0, 5)), font=('Times', 9))]]
    graph_tab = sg.TabGroup([[sg.Tab('Interval', graph_interval),
                              sg.Tab('Labels', graph_label),
                              sg.Tab('Legend', graph_legend),
                              sg.Tab('Parameters', graph_width_and_color)]], tab_border_width=2, size=(30, 290))  # DarkAmber - selected_title_color='green', selected_background_color='gray', tab_background_color='black'
    layout = [[sg.Column([[sg.Listbox(values=[], select_mode='multiple', enable_events=True, size=(20, 6), expand_x=True, key='GraphList', horizontal_scroll=True)],
                          [graph_tab]], size=(255, 480), vertical_alignment='c'),
               sg.Canvas(key='-CANVAS-', size=(600, 400), expand_x=True, expand_y=True)],
              [sg.VPush()],
              [sg.Button('Create graph', tooltip="Create", border_width=2, size=(10, 1), key='GraphCreate'),
               sg.Button('Back', tooltip="Back to processing.", border_width=2, size=(10, 1), key='OutCalc')]]
    return layout


#  OSZICAR files save / preview
def oszicar_mode_GUI():
    layout = [[sg.Multiline('', disabled=True, rstrip=False, horizontal_scroll=True, size=(80, 24), key='TablePreview', font=('Consolas', 10), expand_x=True, expand_y=True)],
              [sg.Button('Build Graphs', size=(20, 1), tooltip='Press', border_width=2, key='GraphMode'),
               sg.Button('Create Excel file', tooltip="Press", border_width=2, size=(20, 1), key='CreateExcel'),
               sg.Button('Back', tooltip="Back to main window.", border_width=2, size=(10, 1), key='Exit')]]
    return layout


#  POSCAR file creation for input step
def poscar_mode_GUI():
    layout = [[sg.Text('Input number of step for creating POSCAR file.', relief=sg.RELIEF_SOLID, expand_x=True, justification='center')],
              [sg.Text('Step:', size=(15, 1)),
               sg.InputText(size=(15, 1), enable_events=True, key='StepPOSCAR', expand_x=True)],
              [sg.Text(f'Max step: -', key='MaxStep')],
              [sg.Text('Type of coordinates: '),
               sg.Combo(['Direct', 'Cartesian'], default_value='Cartesian', key='Coord', readonly=True, expand_x=True)],
              [sg.Text('Choose folder to save:', pad=((5, 0), (5, 5))),
               sg.InputText(size=(20, 1), key='POSCARsave', expand_x=True, pad=((2, 5), (5, 5))),
               sg.FolderBrowse('Select')],
              [sg.Checkbox('Fix coordinates of atoms', default=True, key='FixCoord')],
              [sg.Button('Create file', key='CreatePOSCAR', enable_events=True, size=(8, 1)),
               sg.Push(), sg.Push(), sg.Button('Back', key='ExitPOSCAR', tooltip='Back to main window.', enable_events=True, size=(8, 1))]]
    return layout


#  GUI for POSCAR view mode
def file_choose_window():
    layout = [[sg.Listbox(values=[], size=(30, 6), key='CHOSE')],
              [sg.Button('Ok', key='SUBMIT', enable_events=True, size=(8, 1))]]
    return layout


#  GUI's for work with supercomputer (console, file sharing)
def user_authentication():
    layout = [[sg.Text('Input / choose username:', font='LucidaConsole, 14', relief=sg.RELIEF_SOLID)],
              [sg.Combo(values=[], size=(28, 1), font='LucidaConsole, 12', key='-USERNAME-', enable_events=True)],
              [sg.Button('Submit', border_width=2, size=(10, 1), mouseover_colors='Yellow', key='-AUTHSUBM-')]]
    return layout


def rewrite_file():
    layout = [[sg.Text('Do you want to rewrite file?', font='LucidaConsole, 14', relief=sg.RELIEF_SUNKEN)],
              [sg.Text('Old size: -', size=(48, 1), relief=sg.RELIEF_SOLID)],
              [sg.Text('New size: -', size=(48, 1), relief=sg.RELIEF_SOLID)],
              [sg.Button('Yes for all', enable_events=True, size=(10, 1), border_width=2, key='-YESALL-'),
               sg.Button('Yes', enable_events=True, size=(10, 1), border_width=2, key='-YES-'),
               sg.Button('No', enable_events=True, size=(10, 1), border_width=2, key='-NO-'),
               sg.Button('Cancel', enable_events=True, size=(10, 1), border_width=2, key='-CANCEL-')]]
    return layout


def transfer_progress():
    layout = [[sg.Text('Transferring of: -', expand_x=True, border_width=2, relief=sg.RELIEF_SOLID)],
              [sg.ProgressBar(max_value=100, border_width=2, relief=sg.RELIEF_SOLID, key='-TRANSFER-PROGRESS-', style='winnative', size=(40, 10))],
              [sg.Text('Transferred: {0:>15}; From: {1:>15}'.format('-', '-'), border_width=2, relief=sg.RELIEF_SUNKEN, key='-TRANSFERRINFO-')],
              [sg.Multiline(enable_events=True, visible=False, key='-REROUTE-STDOUT-', reroute_stdout=True, reroute_cprint=True)]]
    return layout


def file_hosting():
    right_click_menu = ['&Right', ['Open', '---', 'Create', ['Folder', 'File'], 'Rename', 'Delete', '---', 'Cancel']]
    layout = [[sg.Button(' ', enable_events=True, border_width=1, key='-CHNGDIR-', image_source=r'VR_icons\chng-dir.ico', font='TimesNewRoman, 5', pad=((5, 2), (1, 1))),
               sg.Button(' ', enable_events=True, border_width=1, key='-REFRESHDIR-', image_source=r'VR_icons\refresh.ico', font='TimesNewRoman, 5', pad=((5, 2), (1, 1)))],
              [TreeMod(data=sg.TreeData(), headings=['Size', 'Changed'], right_click_menu=right_click_menu, auto_size_columns=False, pad=((0, 0), (0, 0)), select_mode=sg.TABLE_SELECT_MODE_EXTENDED, num_rows=27, col0_width=25, col_widths=[7, 12,], key='-LOCALTREE-', show_expanded=False, enable_events=True, vertical_scroll_only=True, justification='left', col0_heading='Name', border_width=3, header_border_width=2, expand_x=True, expand_y=True),
               sg.Column(layout=[[sg.Button('\u25B6\n\u25B6\n\u25B6\n\u25B6', key='-TOSERVER-', border_width=5, size=(2, 4), enable_events=True)],
                                 [sg.Button('\u25C0\n\u25C0\n\u25C0\n\u25C0', key='-TOLOCAL-', border_width=5, size=(2, 4), enable_events=True)]],
                         vertical_alignment='c'),
               TreeMod(data=sg.TreeData(), headings=['Size', 'Changed'], right_click_menu=right_click_menu, auto_size_columns=False, pad=((0, 0), (0, 0)), select_mode=sg.TABLE_SELECT_MODE_EXTENDED, num_rows=27, col0_width=25, col_widths=[7, 12,], key='-SERVERTREE-', show_expanded=False, enable_events=True, vertical_scroll_only=True, justification='left', col0_heading='Name', border_width=3, header_border_width=2, expand_x=True, expand_y=True)],
              [sg.Push(), sg.Push(), sg.Button('Connect to supercomputer', font='LucidaConsole, 10', border_width=3, enable_events=True, key='-CONNECT-', auto_size_button=True)]]
    return layout


def console_window():
    layout = [[sg.Multiline(default_text='Welcome to console window.\n\n>> ', autoscroll=True, border_width=3, size=(98, 20), disabled=True, do_not_clear=True, key='-CONSOLEOUTPUT-', reroute_stdout=True, auto_refresh=True, font='LucidaConsole, 10', expand_y=True, expand_x=True, pad=((0, 0), (0, 0)))],
              [sg.Input(size=(64, 1), border_width=3, font='LucidaConsole, 14', key='-CONSOLEINPUT-', focus=True, enable_events=True, expand_x=True, pad=((0, 0), (0, 0)))]]
    return layout


#  GUI for describing critical mistakes in work of the program
def traceback_window():
    layout = [[sg.Multiline('', key='ERROR', size=(85, 20))],
              [sg.Button('Ok', key='SUBMIT', enable_events=True)]]
    return layout


# File delete ask
def ask_to_delete_file():
    layout = [[sg.Text('Are you sure?', font=10, justification='c', relief=sg.RELIEF_GROOVE, size=(30, 1))],
              [sg.VPush()],
              [sg.Button('Yes', key='-YES-', enable_events=True, size=(5, 1)), sg.Button('No', key='-NO-', enable_events=True, size=(5, 1))]]
    return layout


#  GUI for file redactor
def redactor_window():
    menu = [['&File', ['&Open', '---', '&Save', 'Save As', '---', 'E&xit']], ['&Edit', ['!&Undo', '!&Redo', '---', '!Copy', '!Paste', '---', 'Search']], ['VASP', ['Check POSCAR']]]
    layout = [[sg.Menu(menu, font='TimesNewRoman, 8', key='-MENU-')],
              [sg.Button(' ', enable_events=True, border_width=1, key='-SAVE-', image_source=r'VR_icons\save.ico', font='TimesNewRoman, 4', pad=((5, 2), (1, 1))),
               sg.Button(' ', enable_events=True, border_width=1, key='-SAVEAS-', image_source=r'VR_icons\save_as.ico', font='TimesNewRoman, 4', pad=((2, 2), (1, 1))),
               sg.Button(' ', enable_events=True, border_width=1, key='-UNDO-', disabled=True, image_source=r'VR_icons\undo.ico', font='TimesNewRoman, 4', pad=((2, 2), (1, 1))),
               sg.Button(' ', enable_events=True, border_width=1, key='-REDO-', disabled=True, image_source=r'VR_icons\repeat.ico', font='TimesNewRoman, 4', pad=((2, 2), (1, 1))),
               sg.Button(' ', enable_events=True, border_width=1, key='-COPY-', disabled=True, image_source=r'VR_icons\copy.ico', font='TimesNewRoman, 4', pad=((2, 2), (1, 1))),
               sg.Button(' ', enable_events=True, border_width=1, key='-PASTE-', disabled=True, image_source=r'VR_icons\paste.ico', font='TimesNewRoman, 4', pad=((2, 2), (1, 1))),
               sg.Button(' ', enable_events=True, border_width=1, key='-SEARCH-', image_source=r'VR_icons\search.ico', font='TimesNewRoman, 4', pad=((2, 5), (1, 1)))],
              [sg.Frame(title='',
                        layout=[[sg.InputText(size=(30, 1), enable_events=True, do_not_clear=True, key='-FIND-', pad=((5, 5), (1, 1))),
                                 sg.Push(),
                                 sg.Text('Found - matches.', key='-FIND-MATCHES-', pad=((5, 1), (1, 1))),
                                 sg.Text(text='\u25BC', enable_events=True, relief=sg.RELIEF_RAISED, key='-FIND-DOWN-', pad=((3, 1), (1, 1))),
                                 sg.Text(text='\u25B2', enable_events=True, relief=sg.RELIEF_RAISED, key='-FIND-UP-', pad=((1, 5), (1, 1))),
                                 sg.Text(text='\u2716', enable_events=True, relief=sg.RELIEF_RAISED, key='-FINDER-CLOSE-', pad=((10, 5), (1, 1)))]],
                        expand_x=True, relief=sg.RELIEF_SUNKEN, key='-FINDER-', visible=True, pad=((0, 0), (0, 0)), background_color='#adaa6f')],
              [sg.Multiline(default_text='', border_width=3, size=(100, 30), enable_events=True, horizontal_scroll=True, do_not_clear=True, no_scrollbar=False, font='TimesNewRoman, 10', key='-FILETEXT-', pad=((0, 0), (0, 0)), auto_refresh=True, rstrip=False, expand_x=True, expand_y=True)],
              [sg.Text('Number of selected rows: 0', font='TimesNewRoman, 9', key='-SELCOUNT-', relief=sg.RELIEF_SOLID, border_width=3),
               sg.Push(),
               sg.Text('row: -, column: -', font='TimesNewRoman, 9', key='-POSITION-', relief=sg.RELIEF_SOLID, border_width=3)]]
    return layout


#  Layout for exiting window
def exiting_window(image):
    layout = [[sg.Image(filename=image, expand_x=True)],
              [sg.Text('VaspReader is closing! Bye-Bye!', font='_ 18', text_color='white', background_color='Black', justification='center', expand_x=True)]]
    return sg.Window(title='', layout=layout, no_titlebar=True, background_color='Black', keep_on_top=True, auto_close=True, auto_close_duration=2).read()


#  Bonds calculation window
def bonds_window():
    all_tab = sg.Tab(title='All',
                     layout=[[sg.Text('Bonds radius:'),
                              sg.Spin(values=[f'{0.05 * i:.2f}' for i in range(0, 11)], initial_value=0.15, disabled=True, enable_events=True, key='-ALL-BONDS-RADIUS-', expand_x=True)],
                             [sg.Text('Bonds length:'),
                              sg.Spin(values=[f'{0.1 * i:.1f}' for i in range(0, 51)], initial_value=1.8, disabled=True, enable_events=True, key='-ALL-BONDS-LENGTH-', expand_x=True)],
                             [sg.VPush()],
                             [sg.Button('Submit', expand_x=True, enable_events=True, key='-SUBMIT-ALL-')]])
    selected_bonds_tab = sg.Tab(title='Selected bonds',
                                layout=[[sg.Listbox(values=[], select_mode='multiple', key='-BOND-NAME-CHOOSE-', enable_events=True, expand_x=True, expand_y=True)],
                                        [sg.Combo(values=[], key='-BOND-NAME-', readonly=True, enable_events=True, expand_x=True)],
                                        [sg.Text('Bonds radius:'),
                                         sg.Spin(values=[f'{0.05 * i:.2f}' for i in range(0, 11)], initial_value=0.15, disabled=True, enable_events=True, key='-BONDS-RADIUS-', expand_x=True)],
                                        [sg.Text('Bonds length:'),
                                         sg.Spin(values=[f'{0.1 * i:.1f}' for i in range(0, 51)], initial_value=1.8, disabled=True, enable_events=True, key='-BONDS-LENGTH-', expand_x=True)],
                                        [sg.VPush()],
                                        [sg.Button('Submit', expand_x=True, enable_events=True, key='-SUBMIT-BONDS-')]])
    trajectory_draw_tab = sg.Tab(title='Trajectory',
                                 layout=[[sg.Text('Start:', pad=((5, 10), (5, 5))), sg.Push(), sg.InputText(key='-START-TRAJECTORY-', enable_events=True, expand_x=True)],
                                         [sg.Text('Step: ', pad=((5, 7), (5, 5))), sg.Push(), sg.InputText(key='-STEP-TRAJECTORY-', enable_events=True, expand_x=True)],
                                         [sg.Text('End:  ', pad=((5, 7), (5, 5))), sg.Push(), sg.InputText(key='-END-TRAJECTORY-', enable_events=True, expand_x=True)],
                                         [sg.VPush()],
                                         [sg.Button('Submit', expand_x=True, enable_events=True, key='-SUBMIT-TRAJECTORY-')],
                                         [sg.Button('Clear', expand_x=True, enable_events=True, key='-CLEAR-TRAJECTORY-')]])
    layout = [[sg.Checkbox('Draw bonds', default=False, enable_events=True, key='-BONDS-DRAW-', expand_x=True, pad=((0, 0), (0, 0)))],
              [sg.TabGroup([[all_tab, selected_bonds_tab, trajectory_draw_tab]], size=(240, 520), expand_x=True, expand_y=True, pad=((0, 0), (1, 1)))]]
    return layout


def chgcar_window():
    layout = [[sg.Text('Folder:', key='-CHGCAR-FILENAME-', relief=sg.RELIEF_SOLID, expand_x=True, pad=((0, 0), (0, 0)))],
              [sg.Combo(values=['Spin Up + Spin Down', 'Spin Up - Spin Down'], readonly=True, default_value='Spin Up + Spin Down', key='-CHGCAR-READ-MODE-', expand_x=True, pad=((0, 0), (5, 5))),
               sg.Button('Read', key='-CHGCAR-READ-', enable_events=True, pad=((5, 0), (5, 5)))],
              [sg.ProgressBar(max_value=3, orientation='horizontal', relief=sg.RELIEF_GROOVE, border_width=2, key='-CHGCAR-PROGRESS-', size=(30, 15), pad=((0, 0), (0, 0)), expand_x=True)],
              [sg.Text('Status:', pad=((0, 0), (0, 5))), sg.Push(), sg.Text('', key='-CHGCAR-STATUS-', pad=((0, 0), (0, 5)))],
              [sg.Text('Visualization type:', relief=sg.RELIEF_SOLID, expand_x=True, pad=((0, 0), (0, 0)))],
              [sg.Combo(values=['Points', 'Isosurface'], readonly=True, enable_events=True, default_value='Points', key='-CHGCAR-DRAW-MODE-', pad=((0, 0), (5, 5)), expand_x=True)],
              [sg.Text('Transparent:', pad=((0, 0), (0, 5))), sg.Slider(range=(0, 100), tick_interval=20, default_value=0, size=(36, 15), font=('', 6), enable_events=True, key='-CHGCAR-TRANSPARENT-', expand_x=True, pad=((0, 0), (0, 5)), resolution=1, orientation='horizontal')],
              [sg.Text('Color:', pad=((0, 0), (5, 5))), sg.InputText(key='-CHGCAR-COLOR-', visible=False, enable_events=True), sg.Push(),
               sg.ColorChooserButton(button_text='', button_color='#ffffff', target='-CHGCAR-COLOR-', key='-CHGCAR-COLOR-BUTTON-', size=(14, 1), pad=((0, 0), (5, 5)))],
              [sg.Text('Density value:', pad=((0, 0), (0, 5))),
               sg.Slider(range=(0, 0), default_value=0, disable_number_display=True, size=(36, 15), font=('', 6), key='-CHGCAR-VALUE-', enable_events=True, expand_x=True, disabled=True, pad=((0, 0), (0, 0)), resolution=1, orientation='horizontal')],
              [sg.Text('Value: ', pad=((0, 0), (0, 5))), sg.Push(), sg.Text('', key='-CHGCAR-VALUE-SHOW-', pad=((0, 0), (0, 5)))],
              [sg.Button('Draw', key='-CHGCAR-DRAW-', enable_events=True, pad=((0, 0), (0, 5))), sg.Push(), sg.Button('Close', key='-CHGCAR-CLOSE-', enable_events=True, pad=((0, 0), (0, 5)))]]
    return layout


def egg_window():
    return [[sg.Image(key='-EGGIMAGE-')]]


class TreeMod(sg.Tree):
    def _RightClickMenuCallback(self, event):
        tree = self.Widget


class VRGUI:
    sg.LOOK_AND_FEEL_TABLE['VRGUI'] = {'BACKGROUND': '#c7b5a5', 'TEXT': '#141121', 'INPUT': '#cfac78', 'TEXT_INPUT': '#141121', 'SCROLL': '#c4be00',
                                       'BUTTON': ('#141121', '#c4be00'), 'PROGRESS': sg.DEFAULT_PROGRESS_BAR_COMPUTE, 'BORDER': 2, 'SLIDER_DEPTH': 2, 'PROGRESS_DEPTH': 0, }  # ('#141121', '#c4be00')
    sg.LOOK_AND_FEEL_TABLE['DARKGUI'] = {"BACKGROUND": "#101010", "TEXT": "#fdcb52", "INPUT": "#503e32", "TEXT_INPUT": "#fdcb52", "SCROLL": "#503e32",
                                         "BUTTON": ("#000000", '#c4be00'), "PROGRESS": sg.DEFAULT_PROGRESS_BAR_COMPUTE, "BORDER": 2, "SLIDER_DEPTH": 2, "PROGRESS_DEPTH": 0, }
    try:
        icon_image = r'VR_icons/VR-logo.ico'
        sg.set_global_icon(icon_image)
    except:
        icon_image = None

    def __init__(self, GUI_type, title, return_keyboard_events=False, modal=False, resizable=False, keep_on_top=True, theme='VRGUI', **kwargs):
        sg.theme(theme)
        self.layout = GUI_type()
        if kwargs.get('hide', None) is not None:
            kwargs.pop('hide')
            self.window = sg.Window(title=f'{title}', layout=self.layout, border_depth=2, resizable=resizable, modal=modal, return_keyboard_events=return_keyboard_events, finalize=True, icon=self.icon_image, keep_on_top=keep_on_top, **kwargs)
            self.window.hide()
        else:
            self.window = sg.Window(title=f'{title}', layout=self.layout, border_depth=2, resizable=resizable, modal=modal, return_keyboard_events=return_keyboard_events, finalize=True, icon=self.icon_image, keep_on_top=keep_on_top, **kwargs)
        self.window.set_min_size(self.window.size)

    def __repr__(self):
        return f'Window object: {self.window}, with layout: {self.layout}'

    def testloop(self):
        while True:
            event, value = self.window.read()
            if event == sg.WINDOW_CLOSED:
                self.window.close()
                break

    def window_return(self):
        return self.window


# core_test = VRGUI(processing_GUI, title='TEST', resizable=True).testloop()
