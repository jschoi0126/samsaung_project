import csv
import random
import matplotlib.pyplot as plt

class ProbabilityMerger:
    def __init__(self, parsers, N=2, markov_index=1):
        self.parsers = parsers
        self.markov_index = markov_index
        self.N = N
        self.merged_prob = []

    def build_merged_prob(self):
        self.merged_prob = []
        min_data_size = min([len(p.prob_of_sequence) for p in self.parsers[1:]])

        for i in range(1, len(self.parsers)):
            self.parsers[i].calc_prob_for_each_seq(self.parsers[self.markov_index].p)
            sample_size = int(min_data_size/ (1 and i == self.markov_index or 10))
            sample = random.choices(self.parsers[i].prob_of_sequence, k=sample_size)
            # for sequence, prob in sample:
            for sequence, prob in self.parsers[i].prob_of_sequence:
                self.merged_prob.append([i, sequence, prob])

        self.merged_prob.sort(key=lambda x: x[2], reverse=True)

    def build_confusion_matrix(self, th_idx):
        th_prob = self.merged_prob[th_idx][2]
        TA, FA, TR, FR = 0, 0, 0, 0
        for user, sequence, prob in self.merged_prob:
            if float(prob) >= float(th_prob):
                if int(user) == self.markov_index:
                    TA += 1
                else:
                    FA += 1
            else:
                if int(user) == self.markov_index:
                    FR += 1
                else:
                    TR += 1
        return TA, FA, TR, FR

    def calc_FAR_FRR(self, TA, FA, TR, FR):
        if (TR + FA == 0):
            FAR = 9999
        else:
            FAR = FA / (TR + FA)

        if (TA + FR == 0):
            FRR = 9999
        else:
            FRR = (FR) / (FR + TA) 

        return FAR, FRR

    def plot_FAR_FRR(self, FARs, FRRs):
        plt.plot(FARs, 'b-', label="FAR")
        plt.plot(FRRs, 'r-', label="FRR")
        plt.xlabel('threshold index')
        plt.ylabel('value')
        plt.title(f'[{self.N}-gram] Using Markov of User{self.markov_index}')
        plt.legend(loc='best')
        plt.show()


    def build_every_confusion_matrix(self):
        min_diff = 1
        min_idx = None
        min_FAR = None
        min_FRR = None
        FARs = []
        FRRs = []
        for th_idx in range(len(self.merged_prob)):
            FAR, FRR = self.calc_FAR_FRR(*self.build_confusion_matrix(th_idx))
            diff = abs(FAR - FRR)

            # print(FAR, FRR, diff, th_idx, self.merged_prob[th_idx][2])

            if FAR == 9999 or FRR == 9999 or diff == 1.0:
                break
            FARs.append(FAR)
            FRRs.append(FRR)
            if min_diff > diff:
                min_diff = diff
                min_idx = th_idx
                min_FAR = FAR
                min_FRR = FRR

        # print(f'min diff : {min_diff}\nmin_threshold_idx : {min_idx}\nmin_threshold : {self.merged_prob[min_idx][2]}')
        # print(f'FAR : {min_FAR}, FRR : {min_FRR}')
        # self.plot_FAR_FRR(FARs,FRRs)
        return min_FAR, min_FRR

    def write_merged_prob(self):
        f = open(f'result/{self.N}g_by{self.markov_index}_merged_prob.csv', 'w', newline='')
        writer = csv.writer(f, delimiter=',')
        writer.writerows(self.merged_prob)
