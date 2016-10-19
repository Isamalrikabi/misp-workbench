MySQL export
============

This code aims to export data from the MySQL database into redis

# Requirements

* System requirements to connect to MySQL: `sudo apt-get install libmysqlclient-dev`
* Install required python packages: `sudo pip install -r requirements.txt`
* Configure the connection to MySQL and redis in `config.py`:

    ```python
        user = '<MySQL username>'
        password = '<MySQL user password>'
        host = '<MySQL host>'
        dbname = '<MySQL database name>'
        redis_socket = '<path to the redis socket>'
    ```
* Run a redis server listening on the socket you defined in the config file

## Optional if you want to copy the redis database to another machine

* Connect to redis: `redis-cli -s <path to the redis socket>`
* Save the database with `save`
* Copy the rdb file


# Keys created in the Redis database

## import\_all\_tables

All the following keys are created

``` python
attributes set(ids)
attribute:<attribute_id> hash(all values)
```

``` python
events set(ids)
event:<event_id> hash(all values)
event:<event_id>:tags set(tags)
```

``` python
organisations set(ids)
organisation:<org_id> hash(all values)
```

``` python
threat_levels set(ids)
threat_level:<threatlevel_id> hash(all values)
```

``` python
users set(ids)
user:<user_id> hash(all values)
```

``` python
tags set(tag_names)
<tagname>:events set(event_ids)
```

And the following keys are the indexes for fast access:

``` python
event_attrs:<event_id> set(attribute_ids)
<hashed_value> set(event_ids)
event_vals:<event_id> set(hashed_values)
val:<hashed_value> value(value)
```

## import\_auth

``` python
<authkey> value(<org_id>)
```

## cache\_attributes

``` python
uuid_id hash(<event_uuid>: <event_id>)
hashstore:<hashed_value> set(event_uuids)  # if the sharing isn't limited
hashstore:<orgid>:<hashed_value> set(event_uuids)  # if the sharing is limited
```



