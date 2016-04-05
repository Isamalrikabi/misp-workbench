Bloom filter fast lookup
========================


# Implementation

Use the full content of the MISP MySQL database and helps the analyst to
group the events by adversaries, tools, and any other caracteristics
the analyst wants.

# Requirements

* access to the redis database created by `backend/make_snapshot.py`
* python packages: `pip install -r requirements.txt`

## Optional

In order to pre-group the events, you'll need to go the following:

1. Fetch the misp-galaxy
    * git submodule init
    * git submodule update
2. Index MISP database: `fti.py`
3. Group the event: `auto_group.py`

# Setup webservice to query the database

* Configure the connection to redis in `config.py`:

 ```
redis_socket = '<path to the redis socket>'
 ```

* Run a redis server listening on the socket you defined in the config file
* Run `group_web.py`

