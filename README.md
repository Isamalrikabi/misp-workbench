# MISP Workbench

Tools to export data out of the MISP MySQL database and use and abuse them outside of this platform.

The initial idea behind this code is to help analysts working on cases after the
incident happened and searching for correlation between multiple events.

![Printscreen](/doc/prints.jpg)

# Content

Have a look at each directory and read the documentation for more details:

1. Export data [MySQL into Redis](backend/)
2. Fast lookup against MISP data using the [hashstore database](hashstore/)
3. Query and interract with [groups created from MISP data](grouping/)
