class Cushion:
    """Describes a single item and all its properties."""
    def __init__(self, csv_row: dict):
        self.old_number = csv_row["gammelt varenummer"]
        self.item_name = csv_row["varenavn"]
        self.color = csv_row["farve"]
        self.ean_13 = csv_row["stregkode"]
        self.new_number = csv_row["nyt varenummer"]

        # TODO: Update documentation to point out that the old number can be an empty string

        # if there is no old number, uses the new number instead.
        if self.old_number == "":
            self.old_number = self.new_number
