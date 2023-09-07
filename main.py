import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import askyesno
from datetime import datetime


# Takes a BarTender database file and a similarly formatted corrections file as input and builds a list of known items
# and their attributes. These attributes can then be retrieved by calling the associated method and the item's index in
# the list. The index can be obtained by calling .get_index(barcode).
class Cushion:
    def __init__(self, bartender_path, corrections_path):
        bartender_entries = []
        try:
            with open(bartender_path) as bartender_file:
                for line in bartender_file:
                    bartender_entries.append(line)
            bartender_entries.pop(0)
        except FileNotFoundError:
            messagebox.showerror("Fejl", "Kan ikke finde BarTender filen.")
            raise SystemExit
        self.old_number = []
        self.item_name = []
        self.color = []
        self.ean_13 = []
        self.new_number = []
        for entry in bartender_entries:
            split_entry = entry.split(";")
            self.old_number.append(split_entry[0])
            self.item_name.append(split_entry[1])
            self.color.append(split_entry[2])
            self.ean_13.append(split_entry[3])
            self.new_number.append(split_entry[4][:-1])

        correction_entries = []
        try:
            with open(corrections_path) as corrections_file:
                for line in corrections_file:
                    correction_entries.append(line)
            correction_entries.pop(0)
        except FileNotFoundError:
            messagebox.showerror("Fejl", "Kan ikke finde filen Rettelser.txt.")
            raise SystemExit
        self.wrong_barcodes = []
        self.corrected_barcodes = []
        self.ask_for_color = []
        self.alt_color = []
        for entry in correction_entries:
            split_entry = entry.split(";")
            self.wrong_barcodes.append(split_entry[0])
            self.corrected_barcodes.append(split_entry[1])
            self.ask_for_color.append((bool(int(split_entry[2]))))
            self.alt_color.append(split_entry[3][:-1])
        
        self.barcode_has_been_entered = False
        self.correct_barcode = ""

    # Returns the index of the barcode in question in .ean_13[]
    # This index corresponds to indices in all other item property lists
    def get_index_by_barcode(self, barcode):
        for i, checked_barcode in enumerate(self.ean_13):
            if checked_barcode == barcode:
                return i

    def get_index_by_old_number(self, old_number):
        for i, number in enumerate(self.old_number):
            if number == old_number:
                return i

    def get_old_number(self, index):
        return self.old_number[index]

    def get_item_name(self, index):
        return self.item_name[index]

    def get_color(self, index):
        return self.color[index]

    def get_ean_13(self, index):
        return self.ean_13[index]

    def get_new_number(self, index):
        return self.new_number[index]

    def get_number_of_entries(self):
        return len(self.item_name)

    # Returns True if the barcode is listed in the BarTender database file
    def barcode_is_valid(self, barcode):
        for checked_barcode in self.ean_13:
            if checked_barcode == barcode:
                return True
        return False

    # Returns True if the barcode is known to potentially be incorrect
    def barcode_needs_correcting(self, barcode):
        for checked_barcode in self.wrong_barcodes:
            if checked_barcode == barcode:
                return True
        return False

    # Takes a potentially incorrect barcode as input and returns the correct one
    # In case of doubt (a correct barcode on a potentially incorrect item) asks the user to confirm the color
    def corrected_barcode(self, barcode):
        for i, wrong_barcode in enumerate(self.wrong_barcodes):
            if wrong_barcode == barcode:
                if self.ask_for_color[i]:
                    use_alternative_color = askyesno("Vælg farve", f"Er varens farve {self.alt_color[i]}?")
                    if use_alternative_color:
                        return self.corrected_barcodes[i]
                    else:
                        return self.wrong_barcodes[i]
                return self.corrected_barcodes[i]
    
    def set_barcode_to_use(self, barcode):
        self.correct_barcode = barcode

    def get_barcode_to_use(self):
        return self.correct_barcode


# Reads the entered barcode, checks if it's correct, corrects it if it's not, and displays the item data
def enter_barcode(barcode):
    uncorrected_barcode = ""
    if cushions.barcode_needs_correcting(barcode):
        uncorrected_barcode = barcode
        cushions.set_barcode_to_use(cushions.corrected_barcode(barcode))
    else:
        cushions.set_barcode_to_use(barcode)
    if cushions.barcode_is_valid(cushions.get_barcode_to_use()):
        index = cushions.get_index_by_barcode(cushions.get_barcode_to_use())
        item_name_label_text.config(text=cushions.get_item_name(index))
        color_label_text.config(text=cushions.get_color(index))
        old_number_label_text.config(text=cushions.get_old_number(index))
        new_number_label_text.config(text=cushions.get_new_number(index))
        if uncorrected_barcode == "" or uncorrected_barcode == cushions.get_ean_13(index):
            ean13_label_text.config(text=cushions.get_ean_13(index))
        else:
            ean13_label_text.config(text=f"{uncorrected_barcode} rettes til {cushions.get_ean_13(index)}")
        number_entry_box.focus_set()
        cushions.barcode_has_been_entered = True
    else:
        if scan_entry_box.get() == "":
            messagebox.showerror(title="Fejl", message="Du mangler at scanne en vare.")
        else:
            messagebox.showerror(title="Fejl", message="Ugyldig stregkode.")
            scan_entry_box.delete(0, "end")
        scan_entry_box.focus_set()


# If the barcode is valid sends a specified number of print jobs to the default printer, writes job details to the log
# file and resets the window
def print_barcode():
    if not cushions.barcode_has_been_entered:
        enter_barcode(scan_entry_box.get())
    if not number_entry_box.get().isnumeric() or int(number_entry_box.get()) < 1 or int(number_entry_box.get()) > 105:
        messagebox.showerror(title="Fejl", message="Ugyldigt antal.\nSkal være mellem 1-105.")
        number_entry_box.delete(0, END)
        if not scan_entry_box.get() == "":
            number_entry_box.focus_set()
        return

    if cushions.barcode_is_valid(cushions.get_barcode_to_use()):
        try:
            for i in range(int(number_entry_box.get())):
                os.startfile(f".\\Data\\PDF\\{cushions.get_barcode_to_use()}.pdf", "print")
            write_to_log_file(cushions.get_barcode_to_use())
            scan_entry_box.delete(0, "end")
            number_entry_box.delete(0, "end")
            scan_entry_box.focus_set()
            item_name_label_text.config(text="")
            color_label_text.config(text="")
            old_number_label_text.config(text="")
            new_number_label_text.config(text="")
            ean13_label_text.config(text="")
            cushions.barcode_has_been_entered = False
            cushions.set_barcode_to_use("")
        except FileNotFoundError:
            messagebox.showerror("Fejl", "PDF filen mangler.")


# Prints the item chosen from the dropdown menu in manual mode
def print_manual():
    old_number = "005-" + cushions_drop_down_list.get().split(" ")[0]
    barcode = cushions.get_ean_13(cushions.get_index_by_old_number(old_number))

    if not manual_number_entry_box.get().isnumeric() or int(manual_number_entry_box.get()) < 1 or int(
            manual_number_entry_box.get()) > 105:
        messagebox.showerror(title="Fejl", message="Ugyldigt antal.\nSkal være mellem 1-105.")
        manual_number_entry_box.delete(0, END)
        return
    else:
        try:
            for i in range(int(manual_number_entry_box.get())):
                os.startfile(f".\\Data\\PDF\\{barcode}.pdf", "print")
            write_to_log_file(barcode)
            manual_number_entry_box.delete(0, "end")
        except FileNotFoundError:
            messagebox.showerror("Fejl", "PDF filen mangler.")


# Enters current job details into the log file
def write_to_log_file(barcode):
    current_tab = tab_control.tab(tab_control.select(), "text")
    time_and_date = str(datetime.now())[:-7]
    log_file_line = ""

    log_file_line += cushions.get_item_name(cushions.get_index_by_barcode(barcode)) + ", "
    log_file_line += cushions.get_color(cushions.get_index_by_barcode(barcode)) + ", "
    log_file_line += cushions.get_old_number(cushions.get_index_by_barcode(barcode)) + ", "
    log_file_line += cushions.get_new_number(cushions.get_index_by_barcode(barcode))

    if current_tab == "Scanner":
        log_file_line = f"{time_and_date}: {number_entry_box.get()} x " + log_file_line
        log_file_line += "\n"
    elif current_tab == "Manuel":
        log_file_line = f"{time_and_date}: {manual_number_entry_box.get()} x " + log_file_line
        log_file_line += " (manuel)\n"

    try:
        log_file = open(".\\Data\\log.txt", "a+")
        log_file.write(log_file_line)
        log_file.close()
    except OSError:
        pass


# Runs when changing tabs - if the currect tab is Scanner, sets focus to scan_entry_box
def tab_changed(event):
    tab = event.widget.tab('current')['text']
    if tab == "Scanner":
        scan_entry_box.focus_set()


# Builds a Cushion object containing data on all known items as well as all known problems
cushions = Cushion(".\\Data\\Hay - Hynder.txt", ".\\Data\\Rettelser.txt")

# Builds a list of strings to be shown in the dropdown Combobox in the "Manuel" tab
# Trims unnecessary data to make the line fit into the window
cushions_drop_down_entries = []

for cushion in range(cushions.get_number_of_entries()):
    cushion_entry = ""
    cushion_entry += cushions.get_old_number(cushion)[4:] + " - "
    cushion_entry += cushions.get_item_name(cushion) + " - "
    cushion_entry += cushions.get_color(cushion)

    cushion_entry = cushion_entry.replace(" FR", "")
    cushion_entry = cushion_entry.replace("Palissade ", "")
    cushion_entry = cushion_entry.replace(" textile", "")
    cushion_entry = cushion_entry.replace(" foam", "")

    cushions_drop_down_entries.append(cushion_entry)

# GUI

# Window properties
window = Tk()
window.resizable(False, False)
window.geometry(f"488x402+{window.winfo_screenwidth() // 2 - 250}+{window.winfo_screenheight() // 4}")
window.title("Hyndescanner")
window.iconbitmap(".\\Data\\barcode-scan.ico")

# Declaration of GUI elements

# Tab setup
tab_control = ttk.Notebook(window)
scanner_tab = ttk.Frame(tab_control)
manual_tab = ttk.Frame(tab_control)

tab_control.add(scanner_tab, text="Scanner")
tab_control.add(manual_tab, text="Manuel")

tab_control.bind("<<NotebookTabChanged>>", tab_changed)

# "Scanner" Tab

    # Main elements
scan_prompt_label = Label(scanner_tab, text="Scan en vare:", font=("Segoe UI", "24"))

scan_entry_box = Entry(scanner_tab, width=14, font=("Segoe UI", "32"))
scan_entry_box.bind("<Return>", lambda event: enter_barcode(scan_entry_box.get()))
scan_entry_box.focus_set()

number_frame = Frame(scanner_tab)

input_number_label = Label(number_frame, text="Ønsket antal: ", font=("Segoe UI", "16"))
input_number_label.grid(row=0, column=0)

number_entry_box = Entry(number_frame, width=4, font=("Segoe UI", "16"))
number_entry_box.bind("<Return>", lambda event: print_barcode())
number_entry_box.grid(row=0, column=1)

print_button = Button(scanner_tab, text="Print", command=print_barcode, width=12, font=("Segoe UI", "16"))

    # Item data display
item_name_label_frame = Frame(scanner_tab)
item_name_label = Label(item_name_label_frame, text="Varenavn:", anchor="w", width=16)
item_name_label_text = Label(item_name_label_frame, anchor="w", width=48)
item_name_label.grid(row=0, column=0)
item_name_label_text.grid(row=0, column=1)

color_label_frame = Frame(scanner_tab)
color_label = Label(color_label_frame, text="Farve:", anchor="w", width=16)
color_label_text = Label(color_label_frame, anchor="w", width=48)
color_label.grid(row=0, column=0)
color_label_text.grid(row=0, column=1)

old_number_label_frame = Frame(scanner_tab)
old_number_label = Label(old_number_label_frame, text="Gammelt nummer:", anchor="w", width=16)
old_number_label_text = Label(old_number_label_frame, anchor="w", width=48)
old_number_label.grid(row=0, column=0)
old_number_label_text.grid(row=0, column=1)

new_number_label_frame = Frame(scanner_tab)
new_number_label = Label(new_number_label_frame, text="Nyt nummer:", anchor="w", width=16)
new_number_label_text = Label(new_number_label_frame, anchor="w", width=48)
new_number_label.grid(row=0, column=0)
new_number_label_text.grid(row=0, column=1)

ean13_label_frame = Frame(scanner_tab)
ean13_label = Label(ean13_label_frame, text="Stregkode:", anchor="w", width=16)
ean13_label_text = Label(ean13_label_frame, anchor="w", width=48)
ean13_label.grid(row=0, column=0)
ean13_label_text.grid(row=0, column=1)

# "Manuel" Tab

    # Main elements

choose_cushion_label = Label(manual_tab, text="Vælg type:", font=("Segoe UI", "24"))

cushions_drop_down_list = ttk.Combobox(manual_tab, values=cushions_drop_down_entries)
cushions_drop_down_list.set(cushions_drop_down_entries[0])
cushions_drop_down_list["state"] = "readonly"

manual_number_frame = Frame(manual_tab)

manual_input_number_label = Label(manual_number_frame, text="Ønsket antal: ", font=("Segoe UI", "16"))
manual_input_number_label.grid(row=0, column=0)

manual_number_entry_box = Entry(manual_number_frame, width=4, font=("Segoe UI", "16"))
manual_number_entry_box.bind("<Return>", lambda event: print_manual())
manual_number_entry_box.grid(row=0, column=1)

manual_print_button = Button(manual_tab, text="Print", command=print_manual, width=12, font=("Segoe UI", "16"))

# Placement of GUI elements
tab_control.pack(pady=4)

scan_prompt_label.pack()
scan_entry_box.pack(pady=10)
number_frame.pack()
print_button.pack(pady=16)

item_name_label_frame.pack()
color_label_frame.pack()
old_number_label_frame.pack()
new_number_label_frame.pack()
ean13_label_frame.pack()

choose_cushion_label.pack(pady=12)
cushions_drop_down_list.pack(fill=X, padx=4, pady=10)
manual_number_frame.pack(pady=10)
manual_print_button.pack(pady=16)

window.mainloop()
