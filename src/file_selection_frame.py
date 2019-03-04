from itertools import count as _count
import tkinter as _tk
from tkinter import filedialog as _fd

class FileSelectionFrame(_tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text='Files', padx=5, pady=5)
        
        self.__file_list = []
        self.__previous_selection = []
        self.__on_add_callbacks = []
        self.__on_remove_callbacks = []
        self.__on_selection_callbacks = []
        self.__create_file_list_frame()
        self.__poll_selection()

    @property
    def files(self):
        return list(self.__file_list)

    def trace_file_additions(self, callback):
        self.__on_add_callbacks.append(callback)

    def trace_file_removals(self, callback):
        self.__on_remove_callbacks.append(callback)

    def trace_file_selection_changes(self, callback):
        self.__on_selection_callbacks.append(callback)

    def __create_file_list_frame(self):
        self.__file_list_box = list_box = _tk.Listbox(self)
        list_box.config(width=50, height=30)
        list_box.config(selectmode=_tk.EXTENDED)
        list_box.pack(fill=_tk.BOTH, expand=True)

        button_frame = _tk.Frame(self)
        button_frame.pack()
        
        add_button = _tk.Button(button_frame, width=10, text='Add Files',
                                command=self.__add_files)
        add_button.pack(side=_tk.LEFT, padx=3, pady=3)

        remove_button = _tk.Button(button_frame, width=10, text='Remove Files',
                                   command=self.__remove_files)
        remove_button.pack(side=_tk.LEFT, padx=3, pady=3)

    def __add_files(self):
        selected_files = _fd.askopenfilenames()
        files_to_add = [file for file in selected_files if file not in self.__file_list]

        if files_to_add:
            self.__file_list.extend(files_to_add)
            self.__file_list_box.insert(_tk.END, *files_to_add)
            
            for callback in self.__on_add_callbacks:
                callback(files_to_add)

    def __remove_files(self):
        selection = map(int, self.__file_list_box.curselection())
        removed = []
        
        # Each index has to be adjusted each time an element is removed
        for index in map(lambda i1, i2: i1 - i2, selection, _count()):
            removed.append(self.__file_list.pop(index))
            self.__file_list_box.delete(index)
            
        for callback in self.__on_remove_callbacks:
            callback(removed)

    def __poll_selection(self):
        current_selection = list(map(int, self.__file_list_box.curselection()))
        if self.__previous_selection != current_selection:
            self.__previous_selection = current_selection
            for callback in self.__on_selection_callbacks:
                callback(current_selection)
        self.after(250, self.__poll_selection)
