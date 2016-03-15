# MISP Redis Datastore

Fast and flexible MISP backend using Redis.

# Implementation

Imports all the attributes of a MISP instance (directly from the MySQL database) into a redis database. All the attributes are hashed (sha256) at import. The hashing keeps the redis database small, and the content of the redis database works like a [Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter) which makes it easily sharable with trusted partners.

If an event is only visible to one organisation, the users with an authorization key of this organisation will be the only ones able to query for attributes in this event.

# Usage

The two main use cases are the following:

* Running very fast hundreds or thousands of queries against a MISP instance
* Searching for indicators from an air gapped environment with no access to a remote MISP instance, or on an untrusted computer

# Setup MISP export

* System requirements to connect to MySQL: `apt-get install libmysqlclient-dev`
* Install required python packages: `pip install -r backend/requirements_misp.txt`
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

## Optional if you want to copy the redis database to an other machine

* Connect to redis: `redis-cli -s <path to the redis socket>`
* Save the database with `save`
* Copy the rdb file

# Setup webservice to query the database

* Configure the connection to redis in `backend/config.py`:

 ```
redis_socket = '<path to the redis socket>'
 ```

* Run a redis server listening on the socket you defined in the config file
* Install required python packages: `pip install -r backend/requirements_webservice.txt`
* Run `backend/webservice.py`

# Query the webservice

* Install required python packages: `pip install -r client/requirements.txt`
* Query the database using `client/search.py` (For help: `client/search.py -h`)
