import logging
from peewee import *
from os.path import exists

logging.basicConfig(level=logging.INFO)

if(exists('trakt.db')):
	logging.info('Found existing database')
	first_run = False
else:
	logging.info('DB does not exist, will create a new one')
	first_run = True

db = SqliteDatabase('trakt.db')

# for our purposes we're choosing a subset of the data avilable from the Trakt API and storing those
# rationale: only care about certain things like runtime; can always add fields later if needed

class BaseModel(Model):
	class Meta:
		database = db # This model uses the "trakt.db" database.

class Movies(BaseModel):
	trakt_checkin_id = CharField(primary_key=True)
	trakt_content_id = CharField()
	runtime = IntegerField()
	watched_at = DateTimeField(formats=['%Y-%m-%d %H:%M:%S'])
	movie_title = CharField()

class Shows(BaseModel):
	trakt_checkin_id = CharField(primary_key=True)
	trakt_content_id = CharField()
	watched_at = DateTimeField(formats=['%Y-%m-%d %H:%M:%S'])
	runtime = IntegerField()
	show_title = CharField()
	show_network = CharField()
	episode_title = CharField()
	episode_season = CharField()
	episode_number = CharField()

db.connect()

# safe=True does CREATE IF NOT EXIST
db.create_tables([Movies, Shows], safe=True) if first_run else None



# ---------------

## I initially though of putting both movies + TV in a single table
## but after thinking about it I think it makes sense to split these?
## unsure, need to revisit after writing some queries to see if this works

# class Trakt(Model):
#     trakt_checkin_id = CharField(primary_key=True)
#     trakt_content_id = CharField()
#     watched_at = DateTimeField()
#     content_type = CharField()
#     runtime = IntegerField()
#     movie_title = CharField(null=True)
#     show_title = CharField(null=True)
#     show_network = CharField(null=True)
#     episode_title = CharField(null=True)
#     episode_season = CharField(null=True)
#     episode_number = CharField(null=True)


'''
The API has lots of data but I only care about specific fields:
- checkin_id
- trakt_content_id
- watched_at
- content_type
- runtime
- movie_title
- show_title
- show_network
- episode_title
- episode_season
- episode_number
- genres(?)
'''