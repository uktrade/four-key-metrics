import json
import pprint
from datetime import datetime,timedelta
import time
import ciso8601
import re 
import statistics

with open('data.json') as f:
  data = json.load(f)


to_print = []

for build in data['builds']:
    change_set = []
    if len(build['changeSet']['items']) == 0:
        continue

    environment = build['actions'][0].get('parameters',[{}])[0].get('value')
    if environment != 'production':
        continue

    for change in build['changeSet']['items']:
        date_time = ciso8601.parse_datetime(re.sub(r"^(.*?) (.*?) (.*)$", r"\1T\2\3", change['date']))
        timestamp = time.mktime(date_time.timetuple())
        change_set.append({'timestamp': timestamp})

    deploy_time = int(build['timestamp'])/1000
    to_print.append({
            'result': build['result'],
            'duration': build['duration'],
            'timestamp': deploy_time,
            'environment': environment,
            'change_set': change_set 

        })

pprint.pprint(to_print)


lead_times = []

for deploy in to_print:
    for commit in deploy['change_set']:
        lead_times.append((deploy['timestamp']-commit['timestamp']))

pprint.pprint(lead_times)

pprint.pprint(
        { 'average': str(timedelta(seconds=sum(lead_times) / len(lead_times))),
            'maximum': str(timedelta(seconds=max(lead_times))),
            'minimum': str(timedelta(seconds=min(lead_times))),
            'standard_deviation': str(timedelta(seconds=statistics.pstdev(lead_times)))
            })

print(data['builds'][0].keys())
