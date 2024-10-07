import csv


def save_csv(contacts, output_path):
    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Link', 'Emails', 'Phones'])
        for contact in contacts:
            writer.writerow(contact)
