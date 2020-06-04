import csv
import pprint

class NGramParser:
    N, STOP_WORD, DELIMITER, PADDING = 2, '!', ', ', '__PAD__'

    def __init__(self, user, N=2):
        self.N = N
        self.user = user
        self.reader = csv.reader(open(f'data/{user}_onoff.csv', 'r'))
        # self.reader = csv.reader(open(f'data/{user}_onoff.csv', 'r'))
        self.p = {
            # 'this is': {
            #     'spartan': 0.33333333,
            #     'america': 0.66666666
            # }
        }
        self.num_event_given = {
            # 'this is': {
            #     'spartan': 1,
            #     'america': 2
            # }
        }
        self.num_all_given = {
            # 'this is': 3
        }
        self.onoff = []      # e.x. [ ['com.kakao.talk', 'com.iloen.melon'] , ['com.nhn.android.search']]
        self.prob_of_sequence = []
        self.num_of_sequence = {}
        self.num_of_sequence_size = {
            # size: count
        }
        self.onoff_ngram = []# e.x. [ ['A', 'B'] , ['B', 'C'] , ['C', 'D'], ... ]
        self.app_set = set()
        self.app_appeared_time = {}

    def __parse_ngram(self, sequence):
        if len(sequence) < self.N - 2:
            diff = self.N - 2 - len(sequence)
            sequence += [self.PADDING] * diff

        sequence = [self.STOP_WORD] + sequence + [self.STOP_WORD]
        ngram = []

        for i in range(0, len(sequence) - self.N + 1):
            token: list = sequence[i:i+self.N]
            ngram.append(token)

            given, event = self.DELIMITER.join(token[:-1]), token[-1]
            self.num_event_given[given] = self.num_event_given.get(given, {})
            self.num_event_given[given][event] = self.num_event_given[given].get(event, 0) + 1

        return ngram

    def __add_onoff_and_parse_ngram(self, sequence):
        if len(sequence) == 0:
            return
        self.onoff.append(sequence)
        self.onoff_ngram.append(self.__parse_ngram(sequence))

    def __calc_num_all_given(self):
        self.num_all_given = {}
        for key in self.num_event_given.keys():
            self.num_all_given[key] = sum(self.num_event_given[key].values())

    def __calc_num_of_sequence_size(self):
        for sequence in self.onoff:
            self.num_of_sequence_size[len(sequence)] = self.num_of_sequence_size.get(len(sequence), 0) + 1

    def group_sequence_and_parse_ngram(self):
        sequence = []   # e.x. ['com.kakao.talk', 'com.iloen.melon']
        last_app, current_app = None, None
        for line in self.reader:
            current_app = line[2]
            if len(line[0]) == 0:
                continue

            if line[0] == 'screen_off':
                self.__add_onoff_and_parse_ngram(sequence)
                sequence = []
            elif line[0] == 'screen_on':
                last_app, current_app = None, None
                pass
            elif last_app != current_app:
                # self.app_set.add(current_app)
                self.app_appeared_time[current_app] = self.app_appeared_time.get(current_app, 0) + 1
                sequence.append(current_app)

            last_app = current_app

        self.app_set = set(self.app_appeared_time.keys())
        self.__calc_num_all_given()
        self.__calc_num_of_sequence_size()

    def calc_p(self):
        for given in self.num_event_given:
            for event in self.num_event_given[given]:
                self.p[given] = self.p.get(given, {})
                self.p[given][event] = self.num_event_given[given][event] / self.num_all_given[given]

    def calc_prob_for_each_seq(self, p=None):
        if p == None:
            p = self.p
        prob_of_sequence = {}
        drop = 0
        for i, ngram in enumerate(self.onoff_ngram):
            probability = 1
            sequence = self.onoff[i]
            if len(sequence) < self.N:
                drop += 1
                continue
            for token in ngram:
                given, event = self.DELIMITER.join(token[:-1]), token[-1]
                probability *= p.get(given, {}).get(event, 0)

            seq_str = self.DELIMITER.join(sequence)
            prob_of_sequence[seq_str] = probability
            self.num_of_sequence[seq_str] = self.num_of_sequence.get(seq_str, 0) + 1

        # print(f'[{self.N}-gram] User-{self.user: <2} : {drop: <4} / {len(self.onoff): >4} ({int(drop/len(self.onoff)*100)}%) drop')
        
        self.prob_of_sequence = list(prob_of_sequence.items())
        self.prob_of_sequence.sort(key=lambda x: x[1], reverse=True)