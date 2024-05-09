#Importing libraries

import pandas as pd
import json
import csv
from json import loads, dumps
import ast

#Opening the ChatGPT results and creating a dictionary.
#Must be modified to call correct csv file.
df = pd.read_csv("gpt_results_0.csv")
df = df.drop(columns=['gpt_response', 'missing_icpsr'])
df = df.rename(columns={'icpr_keywords': 'gpt_suggest'})
gpt_results = df.to_dict("records")

#Converting strings of terms to lists to make data easier to parse later.

a = 0
for item in gpt_results:
  stringtolist = gpt_results[a]['gpt_suggest']
  newlist = ast.literal_eval(stringtolist)
  gpt_results[a]['gpt_suggest'] = newlist
  a = a + 1

#Reorganizing data so that each term suggested by ChatGPT is on it's own row.

b = 0
export_dict = []
while b < 400:
  stunum = gpt_results[b]['study_id']
  summ = gpt_results[b]['text']
  gpt_term = gpt_results[b]['gpt_suggest']
  termcount = len(gpt_term)
  c = 0
  while c < termcount:
    export_dict.append(
        {'study_id': stunum, 'summary': summ, 'term': gpt_term[c], 'position': c}
    )
    c = c + 1
  b = b + 1

#Opening ICPSR thesaurus, checking GPT-identified terms against ICPSR thesaurus.
thesaurus = pd.read_csv('thesaurus.csv')
thes = thesaurus['term'].to_list()

result_list = []
for item in export_dict:
  if item['term'] in thes:
    item['thesaurus'] = 'True'
  else:
    item['thesaurus'] = 'False'

#Opening existing ICPSR metadata for comparison.
with open('icpsr_metadata.json') as f:
  icpsr_metadata = json.load(f)

#Checking GPT terms against curator selected terms, also adding study title.
d = 0
for term in export_dict:
  e = 0
  for stu in icpsr_metadata:
    gptno = export_dict[d]['study_id']
    icpsrno = int(icpsr_metadata[e]['study'][0]['identifier'][0])
    if gptno == icpsrno:
      if export_dict[d]['term'] in icpsr_metadata[e]['study'][0]['keyword']:
        export_dict[d]['match'] = 'True'
        export_dict[d]['title'] = icpsr_metadata[e]['study'][0]['title'][0]
      else:
        export_dict[d]['match'] = 'False'
        export_dict[d]['title'] = icpsr_metadata[e]['study'][0]['title'][0]

    else:
      e = e + 1
  d = d + 1

#Exporting data.
export = pd.DataFrame.from_dict(export_dict)
export.to_csv('export.csv', index=False)
#This should be modified if you are running at multiple temperatures.