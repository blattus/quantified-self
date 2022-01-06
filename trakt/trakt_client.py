'''
API client for getting data from the Trakt API. 
The main thing here is handling pagination nicely so I don't have 
to in the application code.
'''

from dotenv import load_dotenv
import logging
import os
import requests
import time

# TODO: log to a file since this will be run as a cron job?
logging.basicConfig(level=logging.INFO)

class Trakt(object):

	def __init__(self):

		# initialize environment and set keys 
		load_dotenv()
		TRAKT_CLIENT_ID = os.environ.get("TRAKT_CLIENT_ID")
		TRAKT_API_SECRET = os.environ.get("TRAKT_API_SECRET") 
		TRAKT_USERNAME = os.environ.get("TRAKT_USERNAME")
		
		self.client_id = TRAKT_CLIENT_ID
		self.api_secret = TRAKT_API_SECRET
		self.trakt_username = TRAKT_USERNAME
		
		# For this app we only care about the user's history so hardcoding 
		# this in the API path. Can revisit if we need other Trakt API methods 
		self.api_endpoint = f'https://api.trakt.tv/users/{TRAKT_USERNAME}/history'

		# We can hardcode the headers required by the API too
		self.api_headers = {
			'Content-type' : 'application/json',
			'trakt-api-key' : TRAKT_CLIENT_ID,
			'trakt-api-version' : '2'
		}

	def get_results(self, start_at=False):
		'''
		get user's watched history from the Trakt API
		can optionally pass `start_at` to limit the lookback of the request

		'''

		# 20 is an arbitrary hardcoded limit (default is 10). From testing,
		# getting 50 extended results takes about 2-3 seconds.
		params = {
			'extended' : 'full',
			'limit' : '50'
		}

		if start_at:
			params['start_at'] = start_at
		
		api_response = []

		# initialize API session + set headers once
		s = requests.Session()
		s.headers.update(self.api_headers)
		
		# make API call
		logging.info('making API request')
		r = s.get(self.api_endpoint, params=params)
		logging.info(f'found {r.headers["X-Pagination-Item-Count"]} total results')

		# [debugging] log the full API response
		logging.debug('API response:\n'+r.text)
		
		# store result in `api_response` that we'll append to for more pages
		api_response.append(r.json())

		# Trakt returns pagination data in response headers so let's store them
		# https://trakt.docs.apiary.io/#introduction/pagination
		current_page = int(r.headers['X-Pagination-Page'])
		total_pages = int(r.headers['X-Pagination-Page-Count'])

		# DEBUG override while testing
		# total_pages = 1

		# handle API pagination
		if total_pages > current_page:
			logging.info(f'found {total_pages} pages; will make additional API requests')

			for page_number in range(2, total_pages + 1):
				logging.info(f'getting data from page {page_number}')

				params['page'] = page_number
				r = s.get(self.api_endpoint, params=params)

				# [debugging] log the full API response
				logging.debug('API response:\n'+r.text)
				
				api_response.append(r.json())

				# Trakt unauthed API has a rate limit of 1000 calls / 5 minutes = 3 RPS
				# https://trakt.docs.apiary.io/#introduction/rate-limiting
				time.sleep(.3)

		# `api_response` is a list containing a list for each page of results 
		return api_response






			



