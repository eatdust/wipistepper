# Wipistepper Package


Python script to create a cloud map for xplanet using satellite images from the Dundee Satellite Receiving Station, Dundee University, UK. This script can also be installed by pip from pypi.

xplanet can use a cloud map to make the earth look more pretty.

There is a free service which create one such cloud map per day. Due to a temporary unavailability of that service this script create_map was developed to automatically download the necessary geostationary images from the Dundee Satellite Receiving Station, Dundee University, UK. To use this service you need an account there (which is free). Also a new cloud map can be created every three hours.

Set your login information in the configuration file (default name for UNIX-like systems: $HOME/.CreateCloudMap/CreateCloudMap.ini, for Windows: %HOME%\.CreateCloudMap\CreateCloudMap.ini):
