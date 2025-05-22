import csv
import os

def find_heart_rate_file():
    for filename in os.listdir():
        if filename.endswith(".heartRate") or filename.endswith(".heartRate.csv"):
            return filename
    return None

def convert_heart_rate_file(input_path):
    output_path = "../skripte/heart.csv"

    with open(input_path, "r") as infile:
        lines = infile.readlines()

    # Skip metadata/header line
    data_lines = lines[1:]

    with open(output_path, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["heartrate", "time"])

        for line in data_lines:
            parts = line.strip().split(",")
            if len(parts) == 2:
                time, heartrate = parts
                if heartrate.isdigit():
                    writer.writerow([heartrate, time])

    print(f"Conversion complete. Output saved to: {output_path}")

if __name__ == "__main__":
    file = find_heart_rate_file()
    if file:
        convert_heart_rate_file(file)
    else:
        print("No .heartRate file found in the current directory.")
