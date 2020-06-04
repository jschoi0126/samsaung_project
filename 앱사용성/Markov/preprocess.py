#!/usr/local/bin/python3
import csv
from datetime import date, datetime

def get_weekday(timestamp):
    return date.fromtimestamp(timestamp/1000).weekday()

def get_hour(timestamp):
    return datetime.fromtimestamp(timestamp/1000).hour

class Preprocessor:
    def __init__(self, uid):
        reader = csv.reader(open(f'data/{uid}_onoff.csv', 'r'), delimiter=',')
        writer = csv.writer(open(f'data/{uid}_processed_onoff.csv', 'w'), delimiter=',')
        classes = []   # e.x. ['com.kakao.talk', 'com.iloen.melon']
        last_app = None
        last_class = None
        app_begin_time = None
        app_last_time = None
        writer.writerow(['user', 'app', 'app_id', 'use_time_ms', 'start_time', 'weekday', 'is_weekend', 'is_a_m', 'hour_quarter', 'class_seq_size', 'num_unique_class'])
        for line in reader:

            if line[0] == 'screen_off':
                usage_time = int(app_last_time) - app_begin_time
                writer.writerow([uid, last_app, abs(hash(last_app)), usage_time, app_begin_time, get_weekday(app_begin_time), get_weekday(app_begin_time) >= 5 and 1 or 0, get_hour(app_begin_time) < 12 and 1 or 0, get_hour(app_begin_time) // 6, len(classes), len(set(classes))])
            elif line[0] == 'screen_on':
                classes = []
                last_app = None
                last_class = None
                app_begin_time = None
                app_last_time = None

            else:
                class_name, event, current_app, timestamp = line[0], line[1], line[2], line[3]
                if last_app != current_app: # 앱 바뀜
                    if last_app != None:
                        usage_time = int(app_last_time) - app_begin_time
                        writer.writerow([uid, last_app, abs(hash(last_app)), usage_time, app_begin_time, get_weekday(app_begin_time), get_weekday(app_begin_time) >= 5 and 1 or 0, get_hour(app_begin_time) < 12 and 1 or 0, get_hour(app_begin_time) // 6, len(classes), len(set(classes))])
                    last_app = current_app
                    last_class = class_name
                    classes = [class_name]
                    app_begin_time = int(timestamp)
                    app_last_time = timestamp
                
                if last_class != class_name: # 클래스 바뀜
                    classes.append(class_name)
                    app_last_time = timestamp
                    last_class = class_name
                else:
                    app_last_time = timestamp


if __name__ == '__main__':
    for i in range(1, 12):
        p = Preprocessor(i)
