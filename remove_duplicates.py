import os

path = os.path.dirname(__file__)

with open(path + '/vins.csv', 'r') as in_file, open(path + '/vins_nodupes.csv', 'w') as out_file:
    seen = set()
    for line in in_file:
        if line in seen: continue

        seen.add(line)
        out_file.write(line)