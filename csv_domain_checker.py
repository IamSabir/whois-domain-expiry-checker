import csv
import whois
import multiprocessing
import os
from tqdm import tqdm

def get_expiry_date(domain):
    try:
        w = whois.whois(domain)
        expiry_date = w.expiration_date
        if isinstance(expiry_date, list):
            expiry_date = ', '.join([str(date) for date in expiry_date])
        return expiry_date
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    # Read domains from the CSV file
    input_file = 'domains.csv'
    output_file = 'temp_domains.csv'
    expiry_file = 'domains_expiry.csv'

    domains = []
    header = []
    expiry_dates = {}

    with open(input_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        header = reader.fieldnames
        if "Expiry Date" not in header:
            header.append("Expiry Date")

        for row in reader:
            domain = row['Domain'].strip()
            domains.append(domain)

    # Create a multiprocessing Pool
    pool = multiprocessing.Pool()

    # Perform the lookup and retrieve expiry dates concurrently with progress bar
    with tqdm(total=len(domains), desc="Processing Domains", unit="domain") as pbar:
        def update_pbar(_):
            pbar.update()

        results = pool.imap_unordered(get_expiry_date, domains)
        for result in results:
            expiry_dates[domains[len(expiry_dates)]] = result
            update_pbar(None)

    # Update the expiry dates in the CSV data
    with open(input_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=header)
            writer.writeheader()
            for row in reader:
                domain = row['Domain'].strip()
                if domain in expiry_dates:
                    row['Expiry Date'] = expiry_dates[domain]
                writer.writerow(row)

    # Replace the original file with the updated file
    os.replace(output_file, expiry_file)

    print(f"Expiry dates have been added to '{input_file}'.")
