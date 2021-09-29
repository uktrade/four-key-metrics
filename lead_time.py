import json
import pprint
from datetime import datetime,timedelta
import time
import ciso8601
import re 
import statistics

with open('data.json') as f:
  data = json.load(f)


production_deploys = []

deploy_dates = []

for build in data['builds']:
    change_set = []
    if len(build['changeSet']['items']) == 0:
        continue

    environment = build['actions'][0].get('parameters',[{}])[0].get('value')
    if environment != 'production':
        continue

    for change in build['changeSet']['items']:
        change_set.append({'timestamp': change['timestamp']/1000})

    duration = int(build['duration'])/1000
    deploy_time = int(build['timestamp'])/1000
    production_deploys.append({
            'result': build['result'],
            'duration': duration,
            'timestamp': deploy_time + duration,
            'environment': environment,
            'change_set': change_set 

        })
    deploy_dates.append(deploy_time)

pprint.pprint(production_deploys)

lead_times = []

for deploy in production_deploys:
    if deploy['result'] != 'SUCCESS':
        continue

    for commit in deploy['change_set']:
        lead_times.append((deploy['timestamp']-commit['timestamp']))

pprint.pprint(lead_times)

pprint.pprint(
        { 'average': str(timedelta(seconds=sum(lead_times) / len(lead_times))),
            'maximum': str(timedelta(seconds=max(lead_times))),
            'minimum': str(timedelta(seconds=min(lead_times))),
            'standard_deviation': str(timedelta(seconds=statistics.pstdev(lead_times))),
            'earliest_deploy': datetime.fromtimestamp(min(deploy_dates)).isoformat(),
            'latest_deploy': datetime.fromtimestamp(max(deploy_dates)).isoformat(),
            })

print(data['builds'][0].keys())
