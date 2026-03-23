import csv

def append_csv(row):

	with open("./data/results.csv", mode='a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(row)

