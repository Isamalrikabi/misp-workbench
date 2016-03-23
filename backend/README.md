# Introduction

This code aims to export data from the MySQL database into redis


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
<orgid>:<hashed_value> set(event_uuids)  # if the sharing is limited
<hashed_value> set(event_uuids)  # if the sharing isn't limited
```



