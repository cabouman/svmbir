# -*- coding: utf-8 -*-
# Copyright (C) 2020-2022 by SVMBIR Developers
# All rights reserved. BSD 3-clause License.

import PySimpleGUI as sg
import os.path
import numpy as np
import napari
import svmbir
import inspect
import yaml
import sys

"""
This file implements a GUI for svmbir, including the capability to load a sinogram, set parameters, 
do a recon (after which any calculated parameters are updated in the GUI), load and save recons and parameters,
and display the sinogram and recon.  

Notation
    kwkeys: list of keyword args in svmbir.recon (e.g, 'num_cols', 'num_rows', etc)
    kwvals: list of default values for the keyward args
    poskeys: list of positional args ('sino', 'angles')
    doc_keys: list of all args in the docstring for svmbir.recon.  Should be kwkeys + poskeys.
    doc_strings: list of doc string entries for each of the entries in doc_keys
    param_groups: Headings for each group of parameters associated with a test
    gui_keys: list of keys indexing into data-holding elements in the gui window
"""


def get_fcn_keys(fcn):
    """
    Get the positional and keyword arguments from a function.
    Args:
        fcn: A function.

    Returns:
        3 lists:
            A list of strings of keys for required, positional arguments.
            A list of strings of keys for keyword arguments.
            A list of strings of default values for keyword arguments.
    """
    sig = str(inspect.signature(fcn))
    args = sig[1:-1].split(', ')  # Separate the signature string into components like 'num_rows' or 'num_rows=None'
    kwargs = [arg for arg in args if '=' in arg]  # Get the components with '=' to signify keyword argument
    kwkeys = [arg.split('=')[0] for arg in kwargs]  # Split each argument at the '=' and take the first part
    kwvals = [arg.split('=')[1].replace("'", "") for arg in kwargs]  # Default values for keyword args
    poskeys = [arg for arg in args if '=' not in arg]  # Positional args
    return poskeys, kwkeys, kwvals


def get_doc_strings(fcn):
    """
    Get the parts of the doc string associated with each argument in a function.
    Args:
        fcn: A function.

    Returns:
        2 lists:
            A list of strings of keys associated with arguments listed in the doc string.
            A list of strings of doc strings for each argument.
    """
    docs = inspect.getmembers(fcn)
    argstring = docs[9][1].split('Args:\n')[1].split('Returns:')[0]
    arglines = argstring.split('\n')
    # Remove leading whitespace up to the primary indent.
    # Secondary indents will be used to determine continuation lines.
    arglines = [line[8:] for line in arglines]

    # Collect the keys and docstrings
    doc_keys = []
    doc_strings = []
    for line in arglines:
        if len(line) == 0:
            continue
        if line[0] != ' ':  # This indicates a new parameter.  Get the key and the docstring from this line.
            doc_strings += [line]
            cur_key = line[0:line.find(' ')]
            doc_keys += [cur_key]
        else:  # This indicates the continuation of a previous line, so append it to the current doc string entry.
            doc_strings[-1] = doc_strings[-1] + '\n' + line
    return doc_keys, doc_strings


class SvmbirGui:
    """
    Class to create and run a gui to interact with svmbir.
    """
    # Common class variables determine which keywords will appear in the gui
    basic_param_keys = ['geometry', 'weight_type', 'dist_source_detector', 'magnification']
    param_groups = ['Recon', 'Geometry', 'Noise', 'QGGMRF', 'System']
    params_by_group = [['sharpness', 'positivity', 'relax_factor', 'max_resolutions', 'stop_threshold', 'max_iterations'],
                       ['num_rows', 'num_cols', 'delta_pixel', 'roi_radius', 'delta_channel', 'center_offset'],
                       ['sigma_y', 'snr_db', 'sigma_x', 'sigma_p'],
                       ['p', 'q', 'T', 'b_interslice'],
                       ['num_threads', 'verbose'],
                      ]

    choose_file_text = '<--- Choose file   \t\t'

    display_sino_key, display_recon_key = ["-DISPLAY_SINO-", "-DISPLAY_RECON-"]
    do_recon_key, save_recon_key, load_recon_key = ["-DO_RECON-", "-SAVE_RECON-", "-LOAD_RECON-"]
    status_key, reset_key, exit_key = ["-STATUS-", "-RESET-", "-EXIT-"]

    float64_params = ['sigma_x', 'sigma_y']  # These parameters are returned as float64 and are converted to floats

    def __init__(self):
        # Define the basic attributes of the window
        self.sg_theme = 'Material1'  # Choices are in LOOK_AND_FEEL_TABLE in PySimpeGUI.py
        self.font1 = ("Arial", 16)
        self.font2 = ("Arial", 14)

        # Get the arguments from svmbir.recon for default values
        self.poskeys, self.kwkeys, self.kwvals = get_fcn_keys(svmbir.recon)

        # Get the docstrings for each argument to use as tooltips
        self.doc_keys, self.doc_strings = get_doc_strings(svmbir.recon)

        self.gui_keys = []

        # Create the gui window
        self.window = self.initialize_window()

        # Populate the default values
        self.set_entries(self.kwkeys, self.kwvals)

        self.values_dict = None
        self.sino_filename = SvmbirGui.choose_file_text
        self.angles_filename = SvmbirGui.choose_file_text
        self.recon_filename = None
        self.sino_data = None
        self.angles_data = None
        self.output_params = None
        self.viewer = None
        self.recon = None
        self.recon_saved = False
        self.run()

    def initialize_window(self):
        """
        Set up the elements of the gui window.
        Returns:
            A PySimpleGUI window.
            Also modifies several instance variables and displays the window.
        """
        sg.theme(self.sg_theme)
        # Labels and entries for required positional parameters
        required_col = []
        for key in self.poskeys:
            tip = self.get_tip(key)
            filename_key = key + '_filename'
            button_key = key + '_button'
            required_col += [[sg.Button(key + ' file', enable_events=True, key=button_key, font=self.font2,
                                        tooltip=tip),
                              sg.Text(self.choose_file_text, size=(27, 1), font=self.font1, enable_events=True,
                                      justification='r', pad=(0, 0), key=filename_key)]]
            self.gui_keys += [filename_key]

        # Labels and entries for basic parameters
        basic_col = []
        for key in SvmbirGui.basic_param_keys:
            tip = self.get_tip(key)
            # Use drop down menus for weight_type and geometry.
            if key == 'weight_type':
                basic_col.insert(1, [sg.Text(key, size=(17, 1), font=self.font1, justification='r', pad=(0, 0)),
                                     sg.Combo(['unweighted', 'transmission', 'transmission_root', 'emission'],
                                              size=(16, 1), key=key, tooltip=tip, font=self.font1)])
            elif key == 'geometry':
                basic_col += [[sg.Text(key, size=(17, 1), font=self.font1, justification='r', pad=(0, 0)),
                               sg.Combo(['parallel', 'fan-curved', 'fan-flat'],
                                        size=(16, 1), key=key, tooltip=tip, font=self.font1)]]
            else:
                basic_col += [[sg.Text(key, size=(17, 1), font=self.font1, justification='r', pad=(0, 0)),
                               sg.InputText(size=(16, 1), key=key, tooltip=tip, font=self.font1)]]
            self.gui_keys += [key]

        # Labels and entries for additional parameters- one column per group/type of parameters
        additional_cols = []
        for param_group, param_list in zip(SvmbirGui.param_groups, SvmbirGui.params_by_group):
            cur_col = [[sg.Text(param_group + ' parameters:', font=self.font1, justification='r')]]

            # Get the parameters for this group and set up a name field and a text entry block in this column
            for key in param_list:
                tip = self.get_tip(key)
                cur_col += [[sg.Text(key, size=(13, 1), font=self.font1, justification='r', pad=(0, 0)),
                             sg.InputText(size=(8, 1), key=key, tooltip=tip, font=self.font1)]]
                self.gui_keys += [key]

            additional_cols += [sg.Col(cur_col, p=0, vertical_alignment='top')]

        image_viewer_column = [
            [sg.Button("Display sinogram", enable_events=True, key=self.display_sino_key, font=self.font2,
                       tooltip='Open a viewer to display the sinogram')],
            [sg.Button("Perform recon", enable_events=True, key=self.do_recon_key, font=self.font2,
                       tooltip='Load sino and angle data, do recon, and return any computed parameters'),
             sg.Button("Display recon", enable_events=True, key=self.display_recon_key, font=self.font2,
                       tooltip='Open a viewer to display the reconstruction'),
             sg.Button('Save recon', enable_events=True, key=self.save_recon_key, font=self.font2,
                       tooltip='Save the reconstruction and associated parameters')],
            [sg.Button('Load recon', enable_events=True, key=self.load_recon_key, font=self.font2,
                       tooltip='Load a reconstruction and associated parameters'),
             sg.Button("Reset", enable_events=True, key=self.reset_key, font=self.font2),
             sg.Button("Exit", enable_events=True, key=self.exit_key, font=self.font2)],
            [sg.Text('Status:', size=(6, 1), font=self.font1, justification='r', pad=(0, 0)),
             sg.Text('Idle', size=(35, 1), font=self.font1, justification='l', pad=(0, 0), key=self.status_key)]
        ]

        layout = [
            [sg.Text('Hover over an element for info', font=self.font1, text_color='green')],
            [
                [sg.Frame('Actions', image_viewer_column, font=self.font1),
                 sg.Frame('Required Parameters', required_col, font=self.font1),
                 sg.Frame('Basic Parameters', basic_col, font=self.font1)],
                sg.Frame('Additional Parameters', [additional_cols], font=self.font1)
            ],
        ]
        return sg.Window("SVMBIR Recon", layout, finalize=True)

    def display_data(self, data, name):
        """
        Launch an external viewer if not already present, then display the given data.
        Args:
            data (ndarray): 3d numpy array
            name (str): Name to display in status bar and in viewer.
        Returns:
            Nothing, but modifies the status display and possibly self.viewer.
        """
        if data is not None:
            if self.viewer is None:
                create_viewer = True
            else:
                create_viewer = False
                try:
                    self.viewer.show()
                except (RuntimeError, AttributeError):
                    create_viewer = True
            if create_viewer:
                self.window[self.status_key].update('Starting viewer', text_color='green')
                self.window.refresh()
                self.viewer = napari.Viewer(ndisplay=2)
            self.viewer.add_image(
                data, name=name, blending='additive', opacity=0.25,
                colormap='turbo')
            self.window[self.status_key].update('Displaying ' + name, text_color='green')
        else:
            self.window[self.status_key].update('No ' + name + ' to display', text_color='red')

    def do_recon(self):
        """
        Returns:
            Nothing, but calls svmbir.recon and sets several instance variables.
        """
        # Get the current parameters
        cur_params = self.get_cur_params()

        # Load any files
        self.sino_filename = self.window['sino_filename'].get()
        try:
            self.sino_data = np.load(self.sino_filename)
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            self.window[self.status_key].update('Sino file not found', text_color='red')
            return
        self.angles_filename = self.window['angles_filename'].get()
        try:
            self.angles_data = np.load(self.angles_filename)
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            self.window[self.status_key].update('Angle file not found', text_color='red')
            return
        cur_params['sino'] = self.sino_data
        cur_params['angles'] = self.angles_data
        output_params = dict()
        cur_params['output_params_dict'] = output_params

        # Do the recon
        self.window[self.status_key].update('Doing recon', text_color="red")
        self.window.refresh()
        try:
            self.recon = svmbir.recon(**cur_params)
        except Exception as e:
            self.window[self.status_key].update(e, text_color="red")
            print(e, file=sys.stderr)
            return

        self.window[self.status_key].update('Recon finished; parameters updated', text_color="green")
        self.recon_saved = False

        # Change some parameters from float64 to float
        for key in SvmbirGui.float64_params:
            output_params[key] = float(output_params[key])

        # Display the updated parameter values, minus sino and angles
        for key in ['sino', 'angles']:
            output_params.pop(key)
        for key in output_params:
            if key in self.gui_keys:
                self.window[key].update(str(output_params[key]))

        self.output_params = output_params

    def load_recon(self):
        """
        Display a dialog box and try to load the chosen files, both the recon and associated parameters.
        The filename chosen should be a .npy file containing a previously computed recon.  The associated
        parameters should be in a file with the same base name but with .yaml extension.
        Returns:
            Nothing, but modifies several instance variables.
        """
        if not self.ok_to_erase('Load new without saving recon?'):
            return

        # Get the recon filename and try to open it
        filename = sg.popup_get_file("Enter a file name (*.npy) for the recon or press 'Browse' to choose",
                                     title='Load recon', size=(80, 1), font=self.font2,
                                     initial_folder=os.getcwd(), default_extension=".npy")
        if filename is None or filename == '':
            return
        try:
            filename = os.path.abspath(filename)
            self.recon = np.load(filename)
            self.recon_filename = filename
            self.recon_saved = True
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            self.window[self.status_key].update('Recon file not found', text_color='red')
            return
        except ValueError as e:
            print(e, file=sys.stderr)
            self.window[self.status_key].update('Unable to load recon file', text_color='red')
            return

        # Load the parameters
        try:
            params_filename = self.recon_filename.split('.npy')[0] + '.yaml'
            self.load_params(filename=params_filename, check_erase=False)
        except (FileExistsError, KeyError, AttributeError):
            return
        self.window[self.status_key].update('Recon and parameters loaded', text_color='green')

    def load_params(self, filename=None, check_erase=True):
        """
        Display a dialog box if needed and try to load the chosen parameters file.
        The filename chosen should be a .yaml file containing parameters.
        Args:
            filename (str): Name of the file to load (should end in .yaml).  If None, then open a file browser.
            check_erase (boolean): If True, then will display a dialog to confirm before overwriting existing params.
        Returns:
            Nothing, but modifies several instance variables.
        """
        if check_erase and not self.ok_to_erase('Load new without saving recon?'):
            return
        if filename is None:
            filename = sg.popup_get_file("Enter a file name (*.yaml) for the parameters or press 'Browse' to choose",
                                         title='Load parameters', size=(80, 1), font=self.font2,
                                         initial_folder=os.getcwd(), default_extension=".yaml")
        if filename is None or filename == '':
            return

        # Try to open the parameter file
        try:
            with open(filename, 'r') as f:
                self.output_params = yaml.safe_load(f)
            for key in self.values_dict:
                if key in self.output_params:
                    self.window[key].update(str(self.output_params[key]))
            for key in ['sino_filename', 'angles_filename']:
                self.window[key].update(str(self.output_params[key]))
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            self.window[self.status_key].update('Recon parameters file not found', text_color='red')
            raise e
        except KeyError as e:
            print(e, file=sys.stderr)
            self.window[self.status_key].update('Unknown entry in parameters file' + str(e), text_color='red')
            raise e
        except AttributeError as e:
            print(e, file=sys.stderr)
            self.window[self.status_key].update('Unable to load params file' + str(e), text_color='red')
            raise e

    def save_recon(self):
        """
        Display a dialog box and try to save both the recon and associated parameters.
        The filename chosen should be a .npy file.  The associated will be save in a file with the same base
        name but with .yaml extension.
        Returns:
            Nothing, but modifies several instance variables.
        """
        if self.recon is None:
            self.window[self.status_key].update('No recon to save', text_color='red')
            return
        # Get the filename
        filename = sg.popup_get_file("Enter a file name (*.npy) for the recon or press 'Save As' to choose",
                                     title='Save recon', size=(80, 1), font=self.font2,
                                     initial_folder=os.getcwd(), save_as=True, default_extension=".npy")
        if filename is None:
            return
        elif len(filename) < 4 or filename[-4:] != '.npy':
            self.window[self.status_key].update('Filename must end in .npy', text_color='red')
            return
        if len(filename) > 8 and filename[-8:] == '.npy.npy':
            filename = filename[-4:]
        # Save the file and then the parameters
        self.recon_filename = os.path.abspath(filename)
        np.save(self.recon_filename, self.recon)

        self.output_params['sino_filename'] = self.sino_filename
        self.output_params['angles_filename'] = self.angles_filename
        self.output_params['recon_filename'] = self.recon_filename
        params_filename = self.recon_filename.split('.npy')[0] + '.yaml'
        with open(params_filename, 'w') as f:
            yaml.safe_dump(self.output_params, f)
        self.recon_saved = True
        self.window[self.status_key].update('Recon and parameters saved', text_color='green')

    def load_file(self, type_name):
        """
        Display a dialog box, and try to load either a sinogram file or an angles file (both in .npy format).
        Args:
            type_name (str): Either 'sino' or 'angles'

        Returns:
            filename (str): The chosen filename.
            data (ndarray or None): The associated data or None if the filename was invalid or the load was cancelled.
        """
        filename = sg.popup_get_file('Choose ' + type_name + ' file (*.npy)', size=(80, 1),
                                     initial_folder=os.getcwd(), font=self.font2)
        try:
            data = np.load(filename)
            self.window[self.status_key].update('Loaded ' + type_name + ' file', text_color='green')
        except (FileNotFoundError, IsADirectoryError):
            print(e, file=sys.stderr)
            self.window[self.status_key].update(type_name + ' file not found', text_color='red')
            data = None
        except TypeError:  # User canceled
            self.window[self.status_key].update(type_name + ' load cancelled', text_color='red')
            data = None
        return filename, data

    def run(self):
        """
        The main event processing loop.
        Returns:
            Nothing, but processes all the events.
        """
        while True:
            event, self.values_dict = self.window.read()

            # Exit
            if event == "Exit" or event == sg.WIN_CLOSED or event == self.exit_key:
                # Check if recon has been saved
                if self.ok_to_erase('Exit without saving recon?'):
                    break

            # Choose sino
            if event == 'sino_button':
                filename, data = self.load_file('sinogram')
                if data is not None:
                    self.sino_filename = filename
                    self.sino_data = data
                    self.window['sino_filename'].update(self.sino_filename)

            # Choose angles
            if event == 'angles_button':
                filename, data = self.load_file('angles')
                if data is not None:
                    self.angles_filename = filename
                    self.angles_data = data
                    self.window['angles_filename'].update(self.angles_filename)

            # Display sino
            elif event == self.display_sino_key:
                self.display_data(self.sino_data, 'sino')

            # Perform recon
            elif event == self.do_recon_key:
                self.do_recon()

            # Load recon
            elif event == self.load_recon_key:
                self.load_recon()

            # Display recon
            elif event == self.display_recon_key:
                self.display_data(self.recon, 'recon')

            # Save recon
            elif event == self.save_recon_key:
                self.save_recon()

            # Reset
            elif event == self.reset_key:
                # Check if recon has been saved
                if not self.ok_to_erase('Reset without saving?'):
                    continue

                # Reset data, parameters and filenames
                self.sino_filename = None
                self.angles_filename = None
                self.recon_filename = None
                self.sino_data = None
                self.output_params = None
                self.recon = None
                self.recon_saved = False
                if self.viewer is not None:
                    try:
                        self.viewer.close()
                    except RuntimeError:
                        pass
                    self.viewer = None
                self.set_entries(self.kwkeys, self.kwvals)
                for key in ['sino_filename', 'angles_filename']:
                    self.window[key].update(SvmbirGui.choose_file_text)
                self.window[self.status_key].update('Everything reset', text_color='red')

        self.window.close()

    def get_cur_params(self):
        """
        Get all of the paramters from the window and convert them to a dictionary compatible with svmbir.recon.
        Returns:
            The dictionary of parameters.
        """
        cur_params = dict()
        for key in self.values_dict:  # Convert any numeric values to floats and 'None' to None, 'True' to True, etc
            try:  # Find the doc string entry for this key and check for int, float, or bool
                key_index = self.doc_keys.index(key)
                cur_doc_string = self.doc_strings[key_index]
                pos_index = max([cur_doc_string.find(argtype) for argtype in ['(int', '(float', '(bool']])
                if pos_index >= 0:
                    cur_params[key] = eval(self.values_dict[key])
            except ValueError:
                pass
        return cur_params

    def get_tip(self, cur_key):
        """
        Get the doc string entry associated with this key
        Args:
            cur_key (string): a string containing the keyword of the argument

        Returns:
            A string containing the docstring for this key or the string 'No doc string entry.'
        """
        if cur_key in self.doc_keys:
            out_tip = self.doc_strings[self.doc_keys.index(cur_key)]
        else:
            out_tip = 'No doc string entry.'
        return out_tip

    def set_entries(self, keys, vals):
        """
        Set the given entries in the window to the given values
        Args:
            keys (string): the keys to set
            vals (string): the corresponding values

        Returns:
            None, but sets the window entries
        """
        for cur_key, cur_val in zip(keys, vals):
            if cur_key in self.gui_keys:
                self.window[cur_key].update(cur_val)

    def ok_to_erase(self, message):
        """
        Display a dialog that asks if it's ok to proceed even if that means erasing unsaved data.
        Called when an unsaved recon would be overwritten.
        Args:
            message (str):  Message to display in pop up box.

        Returns:
            True if the user approves, False if not.
        """
        ok = False
        if self.recon is not None and not self.recon_saved:
            result = sg.popup_ok_cancel(message, font=self.font2)
            if result == 'OK':
                ok = True
        else:
            ok = True
        return ok


if __name__ == "__main__":

    SvmbirGui()
