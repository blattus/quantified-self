This collection of scripts retrieves watched data from the [Trakt](https://trakt.tv) API and stores the results in an SQLite database. I'm using this along with [Metabase](https://metabase.com) to query my show + movie watch history, and maybe to generate some regular reports on my time spent watching stuff. 

You need a Trakt profile, and to use it to log your watching. My preferred way of doing this is manually with the iOS [Watcht](https://apps.apple.com/us/app/watcht-for-trakt/id1396920723) app. The API client in this package doens't handle oauth (yet), so your Trakt profile must be set to public.

To set up:
- Make a copy of `.env.example` and rename to `.env`. Add your trakt username there.
- Create a new Trakt API application [here](https://trakt.tv/oauth/applications) and add the right IDs to `.env` in the right places.
- `pip install -r requirements.txt`, probably in a virtualenv is best
- `python get_trakt_data.py`

When run, the script will create an SQLite DB `trakt.db` in the local directory if one does not exist. Then, it will query the Trakt API to obtain _all_ watched history data for the provided username. The initial run might take a while depending on how much history your account has. For subsequent runs, the script will check the database for the most recent record, retrieve all watched history after that timestamp. 

This is meant to be run as a a regular cron job (I run it nightly). If you do that, each run should take a few seconds at most. 

Note that we're only pulling selected data from the API as shown in [`database_handler.py`](./database_handler.py). There's a lot more availble that might be useful in the future. If you have any requests for things feel free to open an issue and I can consider adding it. 
