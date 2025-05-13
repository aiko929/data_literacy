import csv
import random


class Noiser:
    def __init__(self, time):
        with open(f"csv/{time}/.heart.csv", "r") as input_file:
            # create reader obj:
            csv_reader = csv.reader(input_file)

            # open new file:
            with open(f"csv/{time}/heart.csv", "w+") as output_file:

                csv_writer = csv.writer(output_file)

                # write header:
                for row in csv_reader:
                    csv_writer.writerow(row)

                    # add noise with 10% propability:
                    if random.random() <= 0.1:
                        noise = [0, 1000, -700]
                        csv_writer.writerow([random.choice(noise), row[1]])
        print("Noiser logged")