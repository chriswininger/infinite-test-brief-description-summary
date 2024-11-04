import time
from utils import *
from sql_queries import *

DELAY_BETWEEN_EVENT_QUERIES_SECONDS = 2
DELAY_BETWEEN_QUERIES_WITHIN_EVENT_SECONDS = 1
NUM_SAMPLES_PER_EVENT = 5  # ask for same event n times


def main():
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

    result = generate_sample(event)

    if result is not None:
      prettyPrintResult(result)
      results.append(result)

    time.sleep(DELAY_BETWEEN_EVENT_QUERIES_SECONDS)

  print('done prediction: ', results)
  cur.close()
  conn.close()

  save_html_output('my_output.html', results)
  save_output('my_output.csv', results)


def generate_sample(event):
  result = {
    'title': event[EVENT_TITLE_COL],
    'human': event[EVENT_TITLE_BRIEF_DESC],
    'full': event[EVENT_TITLE_DESC],
    'id': event[EVENT_ID_COL]
  }

  for i in range(0, NUM_SAMPLES_PER_EVENT):
    prompt_response = ask_service_for_summary(event[EVENT_TITLE_DESC])

    if prompt_response is not None:
      predicted_brief_description = prompt_response['summary']
      result['predicted_' + str(i)] = predicted_brief_description

    time.sleep(DELAY_BETWEEN_QUERIES_WITHIN_EVENT_SECONDS)

  return result


def prettyPrintResult(result):
  print('human: ', result['human'])

  for i in range(0, NUM_SAMPLES_PER_EVENT):
    print('predicted: ', result['predicted_' + str(i)])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
  main()
