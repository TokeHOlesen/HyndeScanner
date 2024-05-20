class Cushion:
    """Describes a single item and all its properties."""
    def __init__(self, csv_line: str):
        csv_data = csv_line.split(";")
        self.old_number = csv_data[0]
        self.item_name = csv_data[1]
        self.color = csv_data[2]
        self.ean_13 = csv_data[3]
        self.new_number = csv_data[4]
