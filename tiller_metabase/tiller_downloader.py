import csv
import config
import gspread
import pandas
import sqlite3


def download_tiller_data():
	'''
	Downloads data from a google sheet given a specified cell range and outputs the result to a CSV file.
	'''

	# auth
	gc = gspread.oauth()

	# open Tiller Foundation Template
	sh = gc.open_by_key(config.google_sheet_key)

	# pick a worksheet
	worksheet = sh.worksheet(config.worksheet_name)

	# we know the range for our spreadsheet is all cells from B1 : end so will use cell notation
	entire_worksheet = worksheet.get(config.worksheet_range)
	print('found {} records'.format(len(entire_worksheet)))

	# update header row to change spaces to underscore, remove symbols, and lowercase
	# https://stackoverflow.com/questions/4081217/how-to-modify-list-entries-during-for-loop
	entire_worksheet[0][:] = [item.replace(' ','_').replace('#','number').lower() for item in entire_worksheet[0]]

	# we also need to edit the amount field in each entry to be more numeric
	entire_worksheet = [[x.replace('$','').replace(',','') if i == 3 else x for i, x in enumerate(item)] for item in entire_worksheet]

	# using `w+` as the mode as we want to destructively replace the whole file
	# the google sheet is the source of truth so this is fine
	with open(config.csv_filename, 'w+', newline='') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerows(entire_worksheet)


def convert_to_sqlite():
	'''
	Uses `pandas` to read a CSV file and write it to an sqlite database.

	This script destructively creates a database file and drops the `transactions` table when it runs. 
	'''

	conn = sqlite3.connect('tiller.db')
	df = pandas.read_csv(config.csv_filename)
	df.to_sql('transactions', conn, if_exists='replace', index=False)
	conn.close()

def main():
	download_tiller_data()
	convert_to_sqlite()

if __name__ == '__main__':
	main()