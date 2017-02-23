import matplotlib.pyplot as plt
import numpy as np
import csv


def main():
    with open('./feedback/peter_manual_1_measure_feedback.csv', 'rwb') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            print(row)



    # scatter plot of the feedback given to each measure



if __name__ == '__main__':
    main()
