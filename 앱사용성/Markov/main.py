#!/usr/local/bin/python3

import pprint
import csv
from merger import ProbabilityMerger
from ngram_parser import NGramParser

def writerowsCSV(filename, rows):
    f = open(filename, 'w', newline='')
    writer = csv.writer(f, delimiter=',')
    writer.writerows(rows)

if __name__ == '__main__':
    N = 4
    parsers = [None]
    for i in range(1, 12):
        parsers.append(NGramParser(i, N))
        parsers[i].group_sequence_and_parse_ngram()
        parsers[i].calc_p()
        parsers[i].calc_prob_for_each_seq()
        
        f = open(f'analysis/{i:02}_markov.txt', 'w') # 유저 i의 조건부 확률
        pp = pprint.PrettyPrinter(indent=4, stream=f)
        pp.pprint(parsers[i].p)

        f = open(f'analysis/{i:02}_appset.txt', 'w') # 유저 i가 사용한 앱 목록
        pp = pprint.PrettyPrinter(indent=4, stream=f)
        pp.pprint(parsers[i].app_set)

        f = open(f'analysis/{i:02}_seq_prob.txt', 'w') # 유저 i의 앱 사용 sequence별 markov 값 모두 곱한것
        pp = pprint.PrettyPrinter(indent=4, stream=f)
        pp.pprint(parsers[i].prob_of_sequence)

        # ! 시퀀스별 markov 값 곱한것 in csv
        f = open(f'analysis_csv/{i:02}_seq_prob.csv', 'w')
        writer = csv.writer(f, delimiter=',')
        writer.writerows(parsers[i].prob_of_sequence)

        # ! 시퀀스별 나타난 횟수
        f = open(f'analysis_csv/{i:02}_sequence_appeared_time.csv', 'w')
        writer = csv.writer(f, delimiter=',')
        writer.writerows(sorted(list(parsers[i].num_of_sequence.items()), key=lambda x: x[1], reverse=True))

        # ! 앱별 나타난 횟수
        f = open(f'analysis_csv/{i:02}_app_appeared_time.csv', 'w')
        writer = csv.writer(f, delimiter=',')
        writer.writerows(sorted(parsers[i].app_appeared_time.items(), key=lambda x: x[1], reverse=True)[:30])

        # ! 시퀀스 사이즈별 갯수
        f = open(f'analysis_csv/{i:02}_num_of_sequence_size.csv', 'w')
        writer = csv.writer(f, delimiter=',')
        writer.writerows(sorted(parsers[i].num_of_sequence_size.items(), key=lambda x: x[1], reverse=True)[:30])
        

    for uid in range(1, 12):
        merger = ProbabilityMerger(parsers, N=N, markov_index=uid)
        merger.build_merged_prob()
        merger.write_merged_prob()
        
        avg_FAR = 0
        avg_FRR = 0
        num_try = 1
        for i in range(num_try):
            merger.build_merged_prob()
            FAR, FRR = merger.build_every_confusion_matrix()
            avg_FAR += FAR
            avg_FRR += FRR

        avg_FAR /= num_try
        avg_FRR /= num_try
        print(f'[{N}-gram by User-{uid}] {avg_FAR}, {avg_FRR}')
    # for i, p in enumerate(parsers[1:]):
    #     print(f'#{i+1} : {len(p.prob_of_sequence)}')
    

    '''
    for i in range(1, 12):
        parsers[i].p = parsers[1].p # 유저i 의 conditional probability를 유저1 것으로 교체
        parsers[i].calc_prob_for_each_seq()

        f = open(f'result/{i:02}_seq_prob_with_p1.txt', 'w')
        pp = pprint.PrettyPrinter(indent=4, stream=f)
        pp.pprint(parsers[i].prob_of_sequence) 
    '''