#!/usr/bin/python

from bs4 import BeautifulSoup

input_file = '/Users/lnyang/tmp/SP500-membership.html'
output_file = '/Users/lnyang/tmp/SP500-membership.tsv'

with open(input_file, 'r') as fp:
  content = fp.read()

soup = BeautifulSoup(content)

rows = soup.find_all('tr')

assert len(rows) > 0
headers = [item.text.strip() for item in rows[0].find_all('th')]
print 'headers: %s' % headers

assert len(headers) > 2
assert headers[0] == 'Ticker'
assert headers[1] == 'Company'

with open(output_file, 'w') as fp:
  print >> fp, '\t'.join(headers)
  for i in range(1, len(rows)):
    items = [item.text.strip() for item in rows[i].find_all('td')]
    print >> fp, '\t'.join(items)

