from OLD_GUI import VRGUI
from OLD_Print import VRPrint
from OLD_GUI import graph_processing_GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
import PySimpleGUI as sg
import itertools


class VRGraphsProcessing(VRGUI, VRPrint):
    def __init__(self, dataframe, GUI_type=graph_processing_GUI, title='VaspReader', theme='VRGUI'):
        super(VRGraphsProcessing, self).__init__(GUI_type, title, resizable=True, keep_on_top=False, theme=theme, enable_close_attempted_event=True)
        VRPrint.__init__(self)
        self.graph_name = ''
        self.dataframe = dataframe
        self.include_label = False
        self.event, self.value = None, None
        self.x_lim = [0, max(self.dataframe[self.dataframe.columns[0]])]
        self.y_lim = [None, None]
        self.legend = dict()
        self.label = ['', '']
        self.is_x_limit, self.is_y_limit, self.is_legend, self.is_label = False, False, False, False
        self.width_line, self.color_line = dict(), dict()
        self.fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=110)
        self.fig_canvas_agg = self.draw_figure()

    def draw_figure(self):
        """Function of drawing figures in canvas element."""
        figure_canvas_agg = FigureCanvasTkAgg(self.fig, self.window['-CANVAS-'].TKCanvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    def delete_figure_agg(self):
        """Function of clearing canvas element."""
        self.fig_canvas_agg.get_tk_widget().forget()
        plt.close('all')

    def get_graph(self):
        """Function of drawing plot using matplotlib. Function suggesting user such options as: X and Y setting of
        plot limits, including legend to plot, setting of line width and curve color."""
        if self.fig_canvas_agg:
            self.delete_figure_agg()
        figure = matplotlib.figure.Figure(figsize=(5, 4), dpi=110)
        if self.is_x_limit and self.is_y_limit:
            self.fig_canvas_agg = figure.add_subplot(111, xlim=self.x_lim, ylim=self.y_lim)
        elif self.is_x_limit and not self.is_y_limit:
            self.fig_canvas_agg = figure.add_subplot(111, xlim=self.x_lim)
        elif not self.is_x_limit and self.is_y_limit:
            self.fig_canvas_agg = figure.add_subplot(111, ylim=self.y_lim)
        elif not self.is_x_limit and not self.is_y_limit:
            self.fig_canvas_agg = figure.add_subplot(111)
        for column in self.value['GraphList']:
            self.fig_canvas_agg.plot(self.dataframe[self.dataframe.columns[0]], self.dataframe[column], linewidth=self.width_line[column], color=self.color_line[column])
        if self.is_legend:
            legend = [self.legend[column] for column in self.value['GraphList']]
            figure.legend(legend, loc='upper right')
        axes = figure.gca()
        axes.spines['top'].set_visible(False)
        axes.spines['right'].set_visible(False)
        if self.is_label:
            axes.set_xlabel(self.label[0], fontsize=12, color='black')
            axes.set_ylabel(self.label[1], fontsize=12, color='black')
        return figure

    def column_select_elements_reaction(self, disabled):
        self.window['fromX'].update(disabled=disabled)
        self.window['toX'].update(disabled=disabled)
        self.window['fromY'].update(disabled=disabled)
        self.window['toY'].update(disabled=disabled)
        self.window['Xlim'].update(disabled=disabled)
        self.window['Ylim'].update(disabled=disabled)
        self.window['Reset'].update(disabled=disabled)
        self.window['RenameLegend'].update(disabled=disabled)
        self.window['CurveChoose'].update(disabled=disabled)
        self.window['ColorApply'].update(disabled=disabled)
        self.window['X-axisName'].update(disabled=disabled)
        self.window['Y-axisName'].update(disabled=disabled)

    def auto_rename_legend(self):
        legend_name = self.value['RenameLegend']
        if 'E' in legend_name:
            legend = []
            if 'COM' in legend_name or 'Sum' in legend_name:
                atoms_number = Counter(sorted(legend_name.split('_')[2:][::2]))
                atoms = list()
                for atom in atoms_number:
                    if atoms_number[atom] != 1:
                        atoms.append(f'${atom}_{str(atoms_number[atom])}$' if atoms_number[atom] < 10 else f'{atom}{str(atoms_number[atom])}')
                    else:
                        atoms.append(atom)
                combination_atoms = itertools.permutations(atoms)
                for combination in combination_atoms:
                    if 'COM' in legend_name:
                        legend.append('Translational energy of ' + ''.join(combination))
                        legend.append('Поступательная энергия ' + ''.join(combination))
                    else:
                        legend.append('Summary energy of ' + ''.join(combination))
                        legend.append('Суммарная кинетическая энергия ' + ''.join(combination))
            else:
                legend = ['Kinetic energy of ' + legend_name.split('_')[1],
                               'Кинетическая энергия атома ' + legend_name.split('_')[1]]
            self.window['AutoRename'].update(values=legend)

    def mainloop(self):
        self.window['GraphList'].update(values=self.dataframe.columns[1:])
        refresh = False
        while True:
            self.event, self.value = self.window.read(timeout=10)
            if self.event == 'OutCalc' or self.event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                # if self.fig_canvas_agg:
                #     self.delete_figure_agg()
                self.window.close()
                self.print('Graph window closed.')
                break
            if refresh:
                self.fig = self.get_graph()
                self.fig_canvas_agg = self.draw_figure()
                refresh = False
            if self.event == 'GraphList':
                if self.value['GraphList']:
                    self.column_select_elements_reaction(False)
                    if self.window['RenameLegend']:
                        self.window['LegendName'].update(disabled=False)
                        self.window['LApply'].update(disabled=False)
                else:
                    self.column_select_elements_reaction(True)
                    self.window['LegendName'].update(disabled=True)
                    self.window['LApply'].update(disabled=True)
                    self.window['LineWidth'].update(disabled=True)
                    self.window['ChCurCol'].update(disabled=True)
                    self.window['CurCol'].update(disabled=True)
                self.x_lim = [None, max(self.dataframe[self.dataframe.columns[0]])]
                self.y_lim = [None, None]
                self.is_x_limit, self.is_y_limit, self.is_legend, self.is_label = False, False, True, False
                self.width_line = {column: None for column in self.value['GraphList']}
                self.color_line = {column: None for column in self.value['GraphList']}
                self.legend = {column: column for column in self.value['GraphList']}
                self.window['CurveChoose'].update(values=list(self.legend.keys()))
                self.window['RenameLegend'].update(values=list(self.legend.keys()))
                self.window['LineWidth'].update(disabled=True)
                self.window['ChCurCol'].update(disabled=True)
                self.window['CurCol'].update(disabled=True)
                self.window['ColorApply'].update(disabled=True)
                self.graph_name = '__'.join(self.value['GraphList'])
                refresh = True
            if self.event == 'RenameLegend':
                self.window['LegendName'].update(disabled=False)
                self.window['LegendName'].update(self.legend[self.value['RenameLegend']])
                self.window['AutoRename'].update(disabled=False)
                self.window['LApply'].update(disabled=False)
                self.auto_rename_legend()
            if self.event == 'AutoRename':
                self.window['LegendName'].update(disabled=False)
                self.window['LegendName'].update(self.value['AutoRename'])
                self.window['LApply'].update(disabled=False)
            if self.event == 'LApply':
                for column in self.legend:
                    if column == self.value['RenameLegend']:
                        self.legend[column] = self.value['LegendName']
                self.window['RenameLegend'].update('')
                self.window['RenameLegend'].update(values=list(self.legend.keys()))
                self.window['LegendName'].update('')
                self.window['LegendName'].update(disabled=True)
                self.window['LApply'].update(disabled=True)
                self.window['AutoRename'].update(disabled=True)
                self.window['AutoRename'].update(values=[])
                self.print(f'The name of the legend has been changed. The legend now includes:\n {str(self.value["RenameLegend"])}.')
                refresh = True
            if self.event == 'CurveChoose':
                self.window['LineWidth'].update(disabled=False)
                self.window['ChCurCol'].update(disabled=False)
                self.window['CurCol'].update(disabled=False)
                self.window['ColorApply'].update(disabled=False)
            if self.event == 'LineWidth' and self.value['LineWidth']:
                try:
                    in_as_float = float(self.value['LineWidth'].replace(',', '.'))
                except:
                    if not (len(self.value['LineWidth']) == 1 and self.value['LineWidth'][0] == '-'):
                        self.window['LineWidth'].update(self.value['LineWidth'][:-1])
            if self.event == 'CurCol':
                if self.value['CurCol'] != 'None':
                    self.window['cur_col'].Update(button_color=self.value['CurCol'])
            if self.event == 'ColorApply':
                color = self.value['CurCol']
                if color == '' or color == 'n':
                    color = None
                self.color_line[self.value['CurveChoose']] = color
                if self.value['LineWidth']:
                    try:
                        width = self.value['LineWidth']
                        width = float(width.replace(',', '.'))
                    except ValueError:
                        self.popup('Width value must be number!', title='EmptyFolderNameError')
                    else:
                        self.width_line[self.value['CurveChoose']] = width
                refresh = True
            if self.event == 'GraphCreate':
                if self.value['GraphList']:
                    graphdir = sg.PopupGetFile(message='Input directory to save graph', default_path=self.graph_name, title='Save graph', save_as=True, no_window=True, keep_on_top=True, file_types=(("PNG File", "*.png"), ("JPG File", "*.jpg *.jpeg"), ("EPS File", "*.eps"), ("PDF File", "*.pdf"), ("SVG File", "*.svg"), ("TIFF File", "*.tiff *.tif")))
                    if graphdir:
                        self.fig.savefig(graphdir, bbox_inches='tight', dpi=300)
                        self.print(f'Graph {graphdir.split("/")[-1]} has been created.')
            if self.event == 'Xlim':
                if self.value['fromX']:
                    self.x_lim[0] = float(self.value['fromX'].replace(',', '.'))
                else:
                    self.x_lim[0] = None
                if self.value['toX']:
                    self.x_lim[1] = float(self.value['toX'].replace(',', '.'))
                else:
                    self.x_lim[1] = None
                self.print(f'X-range changed ----> [{str(self.x_lim)}]')
                self.is_x_limit = True
                refresh = True
            if self.event == 'Ylim':
                if self.value['fromY']:
                    self.y_lim[0] = float(self.value['fromY'].replace(',', '.'))
                else:
                    self.y_lim[0] = None
                if self.value['toY']:
                    self.y_lim[1] = float(self.value['toY'].replace(',', '.'))
                else:
                    self.y_lim[1] = None
                self.print(f'Y-range changed ----> [{str(self.y_lim)}]')
                self.is_y_limit = True
                refresh = True
            if self.event == 'Reset':
                self.x_lim = [None, None]
                self.y_lim = [None, None]
                self.is_x_limit, self.is_y_limit = False, False
                self.window['fromX'].update('')
                self.window['toX'].update('')
                self.window['fromY'].update('')
                self.window['toY'].update('')
                self.print('X-range and Y-range reseted.')
                refresh = True
            if self.event == 'LegendIncl':
                self.is_legend = True if self.value['LegendIncl'] else False
                refresh = True
            if self.event == 'LALS':
                self.label[0] = self.value['X-axisName']
                self.label[1] = self.value['Y-axisName']
                self.is_label = True if self.label[0] or self.label[1] else False
                refresh = True
