import csv

with open('AreaNameEnum.csv') as csv_file:
    reader = csv.reader(csv_file)
    locations = {}
    next(reader)
    for row in reader:
        area_no = int(row[0])
        area_name = row[1]

        if(area_no not in locations):
            locations[area_no] = area_name

# print(locations.keys())