import psycopg2
from configparser import ConfigParser
import requests
import csv


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


def save_html_output(file_name, data):
  field_names = data[0].keys()

  prediction_fields = [entry for entry in field_names if entry.startswith("predicted")]

  html_rows = []

  for entry in data:
    title = entry['title']
    full = entry['full']
    human = entry['human']
    event_url = 'https://infinite.industries/events/' + entry['id']

    predictions_html = ''
    for prediction_field in prediction_fields:
      predictions_html += '''
        <p>{}</p>
      '''.format(entry[prediction_field])

    entry_contents = '''
    <div>
      <h2 class="event-title">{title}</h2>
      
      <div class="human-wrapper">
        <label>human: </label>
        <span>{human}</span>
      </div>
      
      <br />
      
      <div class="prediction-wrapper">
        <label>predictions: </label>
        {predictions}
      </div>
      
      <p>
        <a href="{url}">Event Page</a>
      </p>
    </div>
    '''.format(title=title, human=human, predictions=predictions_html, url=event_url)

    html_rows.append(entry_contents)

  full_html = '''
  <html>
  <head>
    <title>test output</title>
    <style type="text/css">
      label {{
        font-weight: bold;
      }}
    </style>
  </head>
  <body>
    {contents}
  </body>
  </html>
  '''.format(contents="\n".join(html_rows))

  with open(file_name, 'w') as file:
    file.write(full_html)
