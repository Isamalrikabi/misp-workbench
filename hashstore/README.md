Hashstore fast lookup
========================


# Implementation

Imports all the attributes of a MISP instance (directly from the MySQL
database) into a redis database. All the attributes are hashed (sha256) at
import. The hashing keeps the redis database small, and the content of the
redis database works like a [Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter)
which makes it easily sharable with trusted partners.

If an event is only visible to one organisation, the users with an authorization
key of this organisation will be the only ones able to query for attributes in this event.

# Usage

The two main use cases are the following:

* Running very fast hundreds or thousands of queries against a MISP instance
* Searching for indicators from an air gapped environment with no access to a
  remote MISP instance, or on an untrusted computer

# Requirements

* access to the redis database created by `backend/make_hashstore.py`
* python packages: `pip install -r requirements.txt`

# Setup webservice to query the database

* Configure the connection to redis in `config.py`:

 ```
redis_socket = '<path to the redis socket>'
 ```

* Run a redis server listening on the socket you defined in the config file
* Run `webservice.py`

# Install the client

* In the directory `client/`

```
    sudo python setup.py install
```

# Query the webservice

* Install required python packages: `sudo pip install -r client/requirements.txt`
* Make sure that the webservice is running
* Query the database using `misp_fast_lookup -h`
* Example : `misp_fast_lookup -s '127.0.0.1' -k AUTHKEY`
* It is the same AUTHKEY that you use for PyMISP
* The result will be the UUID of the MISP event

