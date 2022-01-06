from database_handler import Movies, Shows, first_run, db
import datetime
import logging
from peewee import IntegrityError
from trakt_client import Trakt

logging.basicConfig(level=logging.INFO)

def format_timestamp(timestamp):
	'''
	Converts Trakt's UTC time representation to 'YYYY-MM-DD HH:MM:SS'
	https://stackoverflow.com/questions/6288892/python-how-to-convert-datetime-format
	'''
	# TODO: move into a separate utils module? 
	
	ts = datetime.datetime.strptime(timestamp, '%Y-%m-%d'+'T'+'%H:%M:%S.%f'+'Z')
	formatted_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')

	return formatted_timestamp

def get_most_recent_checkin():
	'''
	Queries DB for most recent checkin to scope future API requests
	'''
	# TODO: could probably write this as a single DB query but getting the latest of each works fine?
	latest_movie = Movies.select().order_by(-Movies.watched_at).get()
	latest_show = Shows.select().order_by(-Shows.watched_at).get()

	most_recent_checkin = max(latest_movie.watched_at, latest_show.watched_at)
	
	return most_recent_checkin

def store_data(api_data):
	'''
	Formats data from the Trakt API and writes it to our SQLite database.
	`get_results` returns a list of lists, with one list for each page of results
	from the Trakt API. each `page` contains a bunch of `checkin`-s 
	'''
	for page in api_data:
		for checkin in page:
			logging.debug(checkin)

			if checkin['type'] == 'episode':
				record = Shows(
					trakt_checkin_id=checkin['id'],
					trakt_content_id=checkin['episode']['ids']['trakt'],
					watched_at=format_timestamp(checkin['watched_at']),
					runtime=checkin['episode']['runtime'],
					show_title=checkin['show']['title'],
					show_network=checkin['show']['network'],
					episode_title=checkin['episode']['title'],
					episode_season=checkin['episode']['season'],
					episode_number=checkin['episode']['number']
					)

			elif checkin['type'] == 'movie': 
				record = Movies(
					trakt_checkin_id=checkin['id'],
					trakt_content_id=checkin['movie']['ids']['trakt'],
					watched_at=format_timestamp(checkin['watched_at']),
					runtime=checkin['movie']['runtime'],
					movie_title=checkin['movie']['title']
					)
			
			# check if record exists otherwise write to DB
			# force_insert required since we're using a non-auto-incrementing primary key
			# TODO: better way to handle this exception for a duplicate entry? probably.
			try:
				result = record.save(force_insert=True)
			except IntegrityError:
				logging.info(f'record {checkin["id"]} already exists. skipping...')
			else:
				logging.info(f'storing new record {checkin["id"]} in database')
				logging.debug('DB result: '+str(result)) # 1 is success
			

def main():
	print(first_run)
	trakt = Trakt()
	if first_run:
		results = trakt.get_results()
	else:
		results = trakt.get_results(start_at=get_most_recent_checkin())

	store_data(results)

	db.close()

if __name__ == '__main__':
	main()
