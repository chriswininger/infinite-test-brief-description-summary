import psycopg2
from configparser import ConfigParser
import requests
import time
import csv

# SELECT AVG(LENGTH(description)) AS average_description_length
# FROM events;
#
# -- average length is 974
#
# SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY LENGTH(description)) AS median_description_length
# FROM events;
#
# -- median 611
#
# Some "Normal" descriptions:
#
# SELECT * FROM events
# WHERE length(description) >= 600 AND length(description)<= 700 AND brief_description is NOT NULL LIMIT 20;
#
# A couple of outliers:
#
# SELECT * FROM events
# WHERE length(description) > 10000 AND brief_description is not null;
#


GET_SOME_MEDIAN_DESCRIPTION_INPUTS = '''
SELECT id, title, description, brief_description FROM events
WHERE length(description) >= 600 AND
  length(description)<= 700 AND
  brief_description is NOT NULL
  AND length(trim(brief_description)) > 0
  LIMIT 30
'''

# there are 2 like this right now
GET_SOME_EXTREME_LARGE_DESCRIPTION_INPUTS = """
SELECT id, title, description, brief_description FROM events
WHERE length(description) > 10000
AND brief_description is not null
AND length(trim(brief_description)) > 0;
"""

EVENT_ID_COL = 0
EVENT_TITLE_COL = 1
EVENT_TITLE_DESC = 2
EVENT_TITLE_BRIEF_DESC = 3


def load_config(filename='database.ini', section='postgresql'):
  parser = ConfigParser()
  parser.read(filename)

  # get section, default to postgresql
  config = {}
  if parser.has_section(section):
    params = parser.items(section)
    for param in params:
      config[param[0]] = param[1]
  else:
    raise Exception('Section {0} not found in the {1} file'.format(section, filename))

  return config


def connect(config):
  """ Connect to the PostgreSQL database server """
  try:
    # connecting to the PostgreSQL server
    with psycopg2.connect(**config) as conn:
      print('Connected to the PostgreSQL server.')
      return conn
  except (psycopg2.DatabaseError, Exception) as error:
    print(error)
    return None


def ask_service_for_summary(full_description):
  body = {'description': full_description}
  response = requests.post('http://localhost:3003/v1/summarization/get-brief-description', json=body)

  if response.status_code >= 200 and response.status_code < 300:
    return response.json()
  else:
    print(f"Request failed with status code: {response.status_code}")
    return None

def save_output(file_name, data):
  field_names = data[0].keys()

  with open(file_name, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)

    # Write the header
    writer.writeheader()

    # Write the data
    for row in data:
      writer.writerow(row)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
  config = load_config()
  conn = connect(config)

  print('connected')

  cur = conn.cursor()

  cur.execute(GET_SOME_MEDIAN_DESCRIPTION_INPUTS)
  median_desc_events = cur.fetchall()

  cur.execute(GET_SOME_EXTREME_LARGE_DESCRIPTION_INPUTS)
  large_desc_events = cur.fetchall()

  print("median_desc_events size: ", len(median_desc_events))
  print("large_desc_events size: ", len(large_desc_events))

  results = []

  for event in median_desc_events + large_desc_events:
    print('-----------')
    print("event title", event[EVENT_TITLE_COL])
    print("")

    prompt_response = ask_service_for_summary(event[EVENT_TITLE_DESC])

    if prompt_response is not None:
      predicted_brief_description = prompt_response['summary']

      results.append({
        'human': event[EVENT_TITLE_BRIEF_DESC],
        'predicted': predicted_brief_description,
        'full': event[EVENT_TITLE_DESC],
        'id': event[EVENT_ID_COL]
      })

      print('human: ', event[EVENT_TITLE_BRIEF_DESC])
      print('predicted: ',  predicted_brief_description)

      time.sleep(5)

  print('done prediction: ', results)
  cur.close()
  conn.close()

  save_output('my_output.csv', results)
