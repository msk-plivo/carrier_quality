import csv
import re

f1 = open('.csv', 'rb')
r1 = csv.reader(f1)

a = []
for rowa in r1:
    a.append(rowa)
