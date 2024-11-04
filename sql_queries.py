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
