# MISP Redis Datastore

Fast and flexible MISP backend using Redis.

# Implementation

Imports all the attributes of a MISP instance (directly from the MySQL database) into a redis database. All the attributes are hashed (sha256) at import. The hashing keeps the redis database small, and the content of the redis database works like a [Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter) which makes it easily sharable with trusted partners.

If an event is only visible to one organisation, the users with an authorization key of this oganisation will be the only ones able to query for attributes in this event. 

# Usage

The two main usecases are the following:

* Running hundreds of queries against a remote MISP instance takes a while
* Searching for indicators from an airgaped environment with no access to a remote MISP instance

# Setup

* System requirements to connect to MySQL: `apt-get install libmysqlclient-dev`
* Install required python packages: `pip install mysql-python sqlalchemy pycrypto redis flask`
* Configure the connection to MySQL and redis in `backend/config.py`: 

 ```python
user = '<MySQL username>'
password = '<MySQL user password>'
host = '<MySQL host>'
dbname = '<MySQL database name>'
redis_socket = '<path to the redis socket>'
 ```
 
 * Run a redis server listening on the socket you defined in the config file
 * Run `backend/make_cache.py`
 * Run `backend/webservice.py`
 * Query the database using `client/search.py` (requires `pip install requests`)
