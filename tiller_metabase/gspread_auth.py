'''
example application showing how to oauth a google account using gspread
taken from https://docs.gspread.org/en/latest/oauth2.html
'''

import gspread

gc = gspread.oauth()

sh = gc.open("Tiller Foundation Template")

print(sh.sheet1.get('A1'))