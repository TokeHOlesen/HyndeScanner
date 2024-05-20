import os
import pymupdf
from CushionClass import Cushion
from warning_messagebox import show_warning


class DataLoader:
    """
    Loads all the relevant data: the item info, the correction data, the labels. Generates label previews
    and combobox contents.
    """
    def __init__(self, bartender_file_path: str, corrections_file_path: str):
        self.bartender_file_path = bartender_file_path
        self.corrections_file_path = corrections_file_path
        # A list of Cushion class objects - one for each known item.
        self.cushions = []
        # A list of ean-13 numbers that must be directly replaced with another number, without user input.
        self.replacements = {}
        # A list of ean-13 numbers that are potentially incorrect and have more than one potential replacement.
        # User input is necessary to find the correct replacement.
        self.multiple_choice_replacements = {}
        # Reads the BarTender file and constructs a Cushion object from each line; appends them to self.cushions
        try:
            with open(bartender_file_path, "r") as bartender_file:
                next(bartender_file)
                for line in bartender_file:
                    self.cushions.append(Cushion(line.strip()))
        except FileNotFoundError:
            show_warning("Fejl", "Kan ikke finde BarTender filen.")
            raise SystemExit
        # Reads the corrections file and saves the wrong and correct barcodes as a key - value pair in self.corrections
        try:
            with open(corrections_file_path, "r") as corrections_file:
                next(corrections_file)
                for line in corrections_file:
                    line = line.strip().split(";")
                    if line[0] == "erstat":
                        wrong_barcode = line[1]
                        correct_barcode = line[2]
                        self.replacements[wrong_barcode] = correct_barcode
                    elif line[0] == "flere":
                        self.multiple_choice_replacements[line[1]] = line[1:]
        except FileNotFoundError:
            show_warning("Fejl", "Filen \"Rettelser.txt\" findes ikke.")
            raise SystemExit

        # Builds two lists of text entries for the Combobox in the Manual tab - one each for old and new numbers.
        self.old_number_combobox_entry_list = self.build_combobox_elements("old")
        self.new_number_combobox_entry_list = self.build_combobox_elements("new")

        # Checks if there exists a .png file for every .pdf file; converts the pdf into png if not.
        for cushion in self.cushions:
            barcode = cushion.ean_13
            if not os.path.isfile(f"Data/PNG/{barcode}.png"):
                self.convert_pdf_to_png(barcode)

    def build_combobox_elements(self, number_type: str) -> list:
        """Builds a list of item data for the combobox in manual mode, using either old or new item numbers."""
        combobox_element_list = []
        for cushion in self.cushions:
            if number_type == "old":
                combobox_entry = f"{cushion.old_number} - {cushion.item_name} - {cushion.color}"
            else:
                combobox_entry = f"{cushion.new_number} - {cushion.item_name} - {cushion.color}"
            combobox_entry = combobox_entry.replace(" FR", "")
            combobox_entry = combobox_entry.replace("Palissade ", "")
            combobox_entry = combobox_entry.replace(" textile", "")
            combobox_entry = combobox_entry.replace(" foam", "")
            combobox_entry = combobox_entry.replace(" for Palissade", "")
            combobox_entry = combobox_entry.replace(" Interliner", "")
            combobox_element_list.append(combobox_entry)
        return combobox_element_list

    @staticmethod
    def convert_pdf_to_png(barcode: str) -> None:
        """Converts PDF into PNG."""
        label_pdf = pymupdf.open(f"Data/PDF/{barcode}.pdf")
        label = label_pdf.load_page(0)
        label_pix = label.get_pixmap(dpi=300)
        label_pix.save(f"Data/PNG/{barcode}.png")

    def item_exists(self, barcode: str) -> bool:
        """Returns True if the barcode exists and is correct."""
        for item in self.cushions:
            if item.ean_13 == barcode:
                return True
        return False

    def get_item_by_barcode(self, barcode: str) -> Cushion:
        """Returns the Cushion class object with the .ean_13 property equal to barcode."""
        for item in self.cushions:
            if item.ean_13 == barcode:
                return item

    def barcode_must_be_replaced(self, barcode: str) -> bool:
        """Returns true if the barcode exists and is known to be incorrect."""
        if barcode in self.replacements:
            return True
        return False

    def get_replacement_barcode(self, barcode: str) -> str:
        """Returns the correct version of an incorrect barcode."""
        return self.replacements[barcode]

    def multiple_replacements_exist(self, barcode: str) -> bool:
        """
        Returns true if the barcode exists, is known to potentially be incorrect and there is more than one
        possible replacement; user input is necessary.
        """
        if barcode in self.multiple_choice_replacements:
            return True
        return False
