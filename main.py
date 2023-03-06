import os
from tkinter import *
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
        for i in range(len(bartender_entries)):
            this_entry = bartender_entries[i].split(";")
            self.old_number.append(this_entry[0])
            self.item_name.append(this_entry[1])
            self.color.append(this_entry[2])
            self.ean_13.append(this_entry[3])
            self.new_number.append(this_entry[4])

        correction_entries = []
        try:
            with open(corrections_path) as corrections_file:
                for line in corrections_file:
                    correction_entries.append(line)
            correction_entries.pop(0)
        except FileNotFoundError:
            messagebox.showerror("Fejl", "Kan ikke finde Rettelser.txt.")
            raise SystemExit
        self.wrong_barcodes = []
        self.corrected_barcodes = []
        self.ask_for_color = []
        self.alt_color = []
        for i in range(len(correction_entries)):
            this_entry = correction_entries[i].split(";")
            self.wrong_barcodes.append(this_entry[0])
            self.corrected_barcodes.append(this_entry[1])
            self.ask_for_color.append((bool(int(this_entry[2]))))
            self.alt_color.append(this_entry[3])

    # Returns the index of the barcode in question in .ean_13[]
    # This index corresponds to indices in all other item property lists
    def get_index(self, barcode):
        for i in range(len(self.ean_13)):
            if self.ean_13[i] == barcode:
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

    # Returns True if the barcode is listed in the BarTender database file
    def barcode_is_valid(self, barcode):
        for i in range(len(self.ean_13)):
            if self.ean_13[i] == barcode:
                return True
        return False

    # Returns True if the barcode is known to potentially be incorrect
    def barcode_needs_correcting(self, barcode):
        for i in range(len(self.wrong_barcodes)):
            if self.wrong_barcodes[i] == barcode:
                return True
        return False

    # Takes a potentially incorrect barcode as input and returns the correct one
    # In case of doubt (a correct barcode on a potentially incorrect item) asks the user to confirm the color
    def corrected_barcode(self, barcode):
        for i in range(len(self.wrong_barcodes)):
            if self.wrong_barcodes[i] == barcode:
                if self.ask_for_color[i]:
                    use_alternative_color = askyesno("Vælg farve", f"Er varens farve\n{self.alt_color[i]}?")
                    if use_alternative_color:
                        return self.corrected_barcodes[i]
                    else:
                        return self.wrong_barcodes[i]
                return self.corrected_barcodes[i]


barcode_has_been_entered = False
correct_barcode = ""


# Reads the entered barcode, checks if it's correct, corrects it if it's not, and displays the item data
def enter_barcode(barcode):
    global barcode_has_been_entered
    global correct_barcode
    incorrect_barcode = ""
    if cushions.barcode_needs_correcting(barcode):
        incorrect_barcode = barcode
        correct_barcode = cushions.corrected_barcode(barcode)
    else:
        correct_barcode = barcode
    if cushions.barcode_is_valid(correct_barcode):
        index = cushions.get_index(correct_barcode)
        item_name_label_text.config(text=cushions.get_item_name(index))
        color_label_text.config(text=cushions.get_color(index))
        old_number_label_text.config(text=cushions.get_old_number(index))
        new_number_label_text.config(text=cushions.get_new_number(index))
        if incorrect_barcode == "" or incorrect_barcode == cushions.get_ean_13(index):
            ean13_label_text.config(text=cushions.get_ean_13(index))
        else:
            ean13_label_text.config(text=f"{incorrect_barcode} rettes til {cushions.get_ean_13(index)}")
        number_entry_box.focus_set()
        barcode_has_been_entered = True
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
    global barcode_has_been_entered
    global correct_barcode
    if not barcode_has_been_entered:
        enter_barcode(scan_entry_box.get())
    if not number_entry_box.get().isnumeric() or int(number_entry_box.get()) < 1 or int(number_entry_box.get()) > 105:
        messagebox.showerror(title="Fejl", message="Ugyldigt antal.\nSkal være mellem 1-105.")
        number_entry_box.delete(0, END)
        if not scan_entry_box.get() == "":
            number_entry_box.focus_set()
        return

    if cushions.barcode_is_valid(correct_barcode):
        try:
            time_and_date = str(datetime.now())[:-7]
            log_file = open(".\\Data\\log.txt", "a+")
            log_file.write(f"{time_and_date}: {number_entry_box.get()} x "
                           f"{cushions.get_item_name(cushions.get_index(correct_barcode))}, "
                           f"{cushions.get_color(cushions.get_index(correct_barcode))}, "
                           f"{cushions.get_old_number(cushions.get_index(correct_barcode))}, "
                           f"{cushions.get_new_number(cushions.get_index(correct_barcode))}")
            log_file.close()
        except OSError:
            pass
        try:
            for i in range(int(number_entry_box.get())):
                os.startfile(f".\\Data\\PDF\\{correct_barcode}.pdf", "print")
            scan_entry_box.delete(0, "end")
            number_entry_box.delete(0, "end")
            scan_entry_box.focus_set()
            item_name_label_text.config(text="")
            color_label_text.config(text="")
            old_number_label_text.config(text="")
            new_number_label_text.config(text="")
            ean13_label_text.config(text="")
            barcode_has_been_entered = False
            correct_barcode = ""
        except FileNotFoundError:
            messagebox.showerror("Fejl", "PDF filen mangler.")


# Builds a Cushion object containing data on all known items as well as all known problems
cushions = Cushion(".\\Data\\Hay - Hynder.txt", ".\\Data\\Rettelser.txt")

# GUI

# Window properties
window = Tk()
window.resizable(False, False)
window.geometry(f"500x396+{window.winfo_screenwidth() // 2 - 250}+{window.winfo_screenheight() // 4}")
window.title("Hyndescanner")
window.iconbitmap(".\\Data\\barcode-scan.ico")

# Declaration of GUI elements
scan_prompt_label = Label(window, text="Scan en vare:", font=("Segoe UI", "24"))

scan_entry_box = Entry(window, width=14, font=("Segoe UI", "32"))
scan_entry_box.bind("<Return>", lambda event: enter_barcode(scan_entry_box.get()))
scan_entry_box.focus_set()

number_frame = Frame(window)

input_number_label = Label(number_frame, text="Ønsket antal: ", font=("Segoe UI", "16"))
input_number_label.grid(row=0, column=0, pady=10)

number_entry_box = Entry(number_frame, width=4, font=("Segoe UI", "16"))
number_entry_box.bind("<Return>", lambda event: print_barcode())
number_entry_box.grid(row=0, column=1, pady=10)

print_button = Button(window, text="Print", command=print_barcode, width=12, font=("Segoe UI", "16"))

item_name_label = Label(window, text="Varenavn:", anchor="w", width=16)
item_name_label_text = Label(window, anchor="w", width=48)
color_label = Label(window, text="Farve:", anchor="w", width=16)
color_label_text = Label(window, anchor="w", width=48)
old_number_label = Label(window, text="Gammelt nummer:", anchor="w", width=16)
old_number_label_text = Label(window, anchor="w", width=48)
new_number_label = Label(window, text="Nyt nummer:", anchor="w", width=16)
new_number_label_text = Label(window, anchor="w", width=48)
ean13_label = Label(window, text="Stregkode:", anchor="w", width=16)
ean13_label_text = Label(window, anchor="w", width=48)

# Placement of GUI elements
scan_prompt_label.place(x=156, y=8)
scan_entry_box.place(x=80, y=64)
number_frame.place(x=160, y=132)
print_button.place(x=174, y=194)

item_name_label.place(x=16, y=266)
color_label.place(x=16, y=290)
old_number_label.place(x=16, y=314)
new_number_label.place(x=16, y=338)
ean13_label.place(x=16, y=362)
item_name_label_text.place(x=132, y=266)
color_label_text.place(x=132, y=290)
old_number_label_text.place(x=132, y=314)
new_number_label_text.place(x=132, y=338)
ean13_label_text.place(x=132, y=362)

window.mainloop()
