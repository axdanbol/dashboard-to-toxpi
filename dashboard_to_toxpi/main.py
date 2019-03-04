from collections import OrderedDict as _OrderedDict
import csv as _csv
import operator as _operator
from pathlib import PurePath as _Path
import tkinter as _tk
from tkinter import filedialog as _fd
from tkinter import messagebox as _mb

from file_selection_frame import FileSelectionFrame as _FileSelectionFrame


class App:
    def __init__(self):
        self.__root = _tk.Tk()

        self.__file_selector = _FileSelectionFrame(self.__root)
        self.__file_selector.pack(fill=_tk.BOTH, expand=True)

        combine_button = _tk.Button(self.__root, width=10, text='Combine',
                                    command=self.__combine_files)
        combine_button.pack()

    def __combine_files(self):
        in_filenames = self.__file_selector.files

        if not in_filenames:
            _mb.showinfo('Information', 'No input files selected',
                         parent=self.__root)
            return

        out_filename = _fd.asksaveasfilename()
        if not out_filename:
            return

        data = [self.__read_data(filename) for filename in in_filenames]
        data = self.__combine_data(data)
        self.__write_data(out_filename, data)

    def __read_data(self, filename):
        getter = _operator.itemgetter(
            'assayEndpointName', 'CASRN', 'ChemicalName', 'modlGa')

        with open(filename, newline='') as file:
            reader = _csv.DictReader(file)
            data = [getter(line) for line in reader]

        if not data:
            return (filename, '', _OrderedDict(), {}, {})

        endpoint = data[0][0]
        ids = _OrderedDict()
        mapped_names = {}
        mapped_data = {}
        for _unused, casrn, chem_name, value in data:
            ids[casrn] = True
            mapped_names[casrn] = chem_name
            mapped_data[casrn] = value

        return (filename, endpoint, ids, mapped_names, mapped_data)

    def __combine_data(self, data):
        filenames = []
        endpoints = []
        ids = _OrderedDict()
        mapped_names = {}
        mapped_data = {}
        counter = 0

        for file, endpoint, idents, names, values in data:
            filenames.append(_Path(file).stem)
            endpoints.append(endpoint)
            ids.update(idents)
            mapped_names.update(names)
            for casrn, value in values.items():
                if casrn not in mapped_data:
                    mapped_data[casrn] = counter * ['NA']
                if len(mapped_data[casrn]) < counter:
                    missing_count = counter - len(mapped_data[casrn])
                    mapped_data[casrn].extend(missing_count * ['NA'])
                mapped_data[casrn].append(value if float(value) != 0 else 1000000)
            counter += 1

        for value in mapped_data.values():
            if len(value) < counter:
                value.extend((counter - len(value)) * ['NA'])

        return (filenames, endpoints, ids, mapped_names, mapped_data)

    def __write_data(self, filename, data):
        counter = 1
        filenames, endpoints, ids, mapped_names, mapped_data = data
        num_rows = len(filenames)

        with open(filename, 'w', newline='') as file:
            writer = _csv.writer(file, quoting=_csv.QUOTE_NONNUMERIC)

            # Write special rows
            writer.writerow(4 * [''] + num_rows * [1])
            writer.writerow(4 * [''] + filenames)
            writer.writerow(4 * [''] + num_rows * ['Assay'])
            writer.writerow((4 + num_rows) * [''])
            writer.writerow(['row_order', 'chemical_source_sid',
                             'casrn', 'chemical_name'] + endpoints)

            for ident in ids.keys():
                writer.writerow([counter, '', '*' + ident, mapped_names[ident]] +
                                mapped_data[ident])
                counter += 1


if __name__ == '__main__':
    app = App()
    _tk.mainloop()
