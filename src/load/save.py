import csv


def save_csv(contacts, output_path):
    with open(f"cache/{output_path}", "w", newline="") as file:
        writer = csv.writer(file)
        for contact in contacts:
            writer.writerow(contact)
