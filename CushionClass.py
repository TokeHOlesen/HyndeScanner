class Cushion:
    """Describes a single item and all its properties."""
    def __init__(self, csv_line: str, column_name_indices: dict):
        csv_data = csv_line.split(";")
        self.old_number = csv_data[column_name_indices["gammelt varenummer"]]
        self.item_name = csv_data[column_name_indices["varenavn"]]
        self.color = csv_data[column_name_indices["farve"]]
        self.ean_13 = csv_data[column_name_indices["stregkode"]]
        self.new_number = csv_data[column_name_indices["nyt varenummer"]]
