# This program requests and displays the currency exchange rate established by
# the National bank of Ukraine to a selected date. Also includes a basic conversion tools

# pyinstaller -F --windowed main_reminder.py
import tkinter as tk
from tkinter import ttk
import configparser
from tkcalendar import DateEntry
import requests
from datetime import datetime
import pyperclip


class Main_Class:
    def __init__(self, master):
        master.title("Currency converter")
        self.input_frame = ttk.Frame(master, borderwidth=1, relief='groove')

        # Set current conversion currency
        self.conversion_from_uah = True
        # Get the list of currencies of interest
        self.get_currency_list()

        # Create ui
        self.calculate_btn = ttk.Button(self.input_frame, text="Get rate", command=self.get_rate)

        self.currency = ttk.Combobox(self.input_frame, values=self.currency_list, width=5, state="readonly")
        self.currency.bind('<<ComboboxSelected>>', self.currency_selected)
        self.currency.current(0)

        self.date = DateEntry(self.input_frame, width=10, background='green',
                              foreground='white', borderwidth=2, locale='UK_UA')
        self.date.bind('<<DateEntrySelected>>', self.date_selected)
        self.date.bind('<Return>', self.date_selected)

        self.rate_lbl_var = tk.StringVar()
        self.rate_lbl = ttk.Entry(self.input_frame, width=10, textvariable=self.rate_lbl_var, state='readonly',
                                  background='#00FF80')

        self.status_frame = tk.Frame(master)
        self.status = ttk.Label(self.status_frame, text='', borderwidth=1, relief='sunken', anchor='center',
                                foreground='green')
        self.copy_rate = ttk.Button(self.input_frame, text="Copy", command=self.copy_data, width=5)

        # self.exchange_frame = tk.Frame(master,borderwidth=1, relief='groove')
        self.from_entry_var = tk.StringVar()
        # self.from_entry_var.trace_add("write", self.convert())
        self.from_entry = ttk.Entry(self.input_frame, width=10, textvariable=self.from_entry_var)
        self.from_entry.bind('<Return>', self.convert)

        self.to_entry_var = tk.StringVar()
        self.to_entry = ttk.Entry(self.input_frame, width=10, textvariable=self.to_entry_var, state='readonly')

        self.convert_btn = ttk.Button(self.input_frame, width=10, text='Convert', command=self.convert)
        self.swap_btn = ttk.Button(self.input_frame, width=4, text='<=>', command=self.swap_currency)

        self.from_currency_var = tk.StringVar(value='UAH')
        self.from_currency = ttk.Label(self.input_frame, textvariable=self.from_currency_var)
        self.to_currency_var = tk.StringVar(value='USD')
        self.to_currency = ttk.Label(self.input_frame, textvariable=self.to_currency_var)

        ########### Organise layout ###########################
        # self.exchange_frame.pack(expand=True, fill='x', side='right', padx=0, pady=10)
        self.input_frame.pack(padx=10, pady=10, expand=True)
        # self.input_frame.columnconfigure(0, weight=1)

        # self.calculate_btn.grid(row=2, column=0, padx=5, pady=5)
        self.currency.grid(row=0, column=0, padx=5, pady=5)
        self.date.grid(row=0, column=1, padx=5, pady=5)
        self.rate_lbl.grid(row=1, column=0, padx=5, pady=5)
        self.copy_rate.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        self.from_currency.grid(row=0, column=2)
        self.to_currency.grid(row=0, column=4)
        self.from_entry.grid(row=1, column=2, padx=5, pady=5)
        self.to_entry.grid(row=1, column=4, padx=5, pady=5)
        # self.convert_btn.grid(row=2, column=2,columnspan=3, padx=5, pady=5)
        self.swap_btn.grid(row=1, column=3, padx=5, pady=5)

        self.status_frame.pack(expand=True, fill='x')

        self.status.pack(fill='x')
        self.get_rate()

    def date_selected(self, *args):
        # request rate
        self.get_rate()
        self.convert()  # convert

    def currency_selected(self, *args):
        # Change currency in the exchange
        if self.conversion_from_uah:
            self.to_currency_var.set(self.currency.get())
        else:
            self.from_currency_var.set(self.currency.get())
        # request rate
        self.get_rate()
        self.convert()  # convert

    def swap_currency(self):
        # Swap currencies in the exchange field
        from_now = self.from_currency_var.get()
        to_now = self.to_currency_var.get()
        self.from_currency_var.set(to_now)
        self.to_currency_var.set(from_now)
        self.conversion_from_uah = not self.conversion_from_uah  # keep track of conversion from uah or to uah

        # Call convert
        self.convert()

    def convert(self, *args):
        # Convert UAH to selected currency and vice versa
        if self.from_entry_var.get():
            if self.conversion_from_uah:
                converted_val = float(self.from_entry_var.get()) / float(self.rate_lbl_var.get())
            else:
                converted_val = float(self.from_entry_var.get()) * float(self.rate_lbl_var.get())
            self.to_entry_var.set("{:.2f}".format(converted_val))

    def copy_data(self):
        # Copy the exchange rate into the memory
        pyperclip.copy(self.rate_lbl.get())

    def get_rate(self):
        # Convert date to form proper request
        dto = datetime.strptime(self.date.get(), '%d.%m.%y')
        date = datetime.strftime(dto, '%Y%m%d')
        try:
            r = requests.get('https://bank.gov.ua/NBUStatService/v1/statdirectory/exchangenew?json',
                             params={'valcode': self.currency.get(), 'date': date})
            reply = r.json()
        except:
            self.status.config(text='Request error', foreground='red')
            return
        if r.status_code == 200 and len(reply) == 1:
            self.rate_lbl_var.set(reply[0]['rate'])
            self.status.config(text='Success', foreground='green')
        else:
            self.status.config(text='Error. Status code: ' + str(r.status_code) + '. Elements: ' + str(len(reply)),
                               foreground='red')

    def get_currency_list(self):
        # Read the list of currencies from the Params.ini file or create one
        self.config = configparser.ConfigParser()

        if self.config.read('params.ini', encoding='utf-8'):
            self.currency_list = list(dict(self.config.items('Params')).values())
        else:
            self.config['Params'] = {'C0': 'USD', 'C1': 'EUR'}
            with open('params.ini', 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            self.currency_list = ['USD', 'EUR']


if __name__ == "__main__":
    master = tk.Tk()
    MC = Main_Class(master)
    master.mainloop()
