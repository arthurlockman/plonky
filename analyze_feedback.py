import matplotlib.pyplot as plt
import numpy as np
import csv


def main():
    with open('./feedback/peter_manual_1_measure_feedback.csv', 'rwb') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        print('min, max, mean, standard deviation, mode')
        for i, v in enumerate(reader):
            measure_hash, feedback = v
            feedback = eval(feedback)
            feedback_sums = []
            for measure in feedback:
                sum_for_measure = 0
                for f in measure:
                    sum_for_measure += f[1]
                feedback_sums.append(sum_for_measure)

            genome = ""
            for j in range(0, len(measure_hash), 2):
                genome += str(int(measure_hash[j:j + 2])) + ", "
            genome = genome[0:len(genome) - 2]

            plt.figure()
            plt.title("Feed back on genome: %s" % genome)
            plt.xticks(range(-8, 8))
            plt.hist(feedback_sums, bins=list(range(-8, 8)))

            (values, counts) = np.unique(feedback_sums, return_counts=True)
            ind = np.argmax(counts)
            print('%i, %i, %.3f, %.3f, %i' %
                  (min(feedback_sums),
                   max(feedback_sums),
                   np.average(feedback_sums),
                   np.std(feedback_sums),
                   feedback_sums[ind]))

        # plt.show()



    # scatter plot of the feedback given to each measure



if __name__ == '__main__':
    main()
