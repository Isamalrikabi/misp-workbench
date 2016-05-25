# MISP Workbench

Tools to export data out of the MISP MySQL database and use and abuse them in other
systems, mostly for analysts but incident responders should keep an eye on it.

![Printscreen](/doc/prints.jpg)

# Content

Have a look at each directory for more details on what they contain and how to use the
script inside:

*  At first, you should look at exporting data [from MySQL into Redis](backend/)
* [Hashstore database](hashstore/) to do fast lookups against MISP data
* Query and interract with [groups created with MISP data](grouping/) (uses adversaries and tools listed in [MISP galaxy](https://github.com/MISP/misp-galaxy))
