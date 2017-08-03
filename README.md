----------------------------------------------Surface Geology Reader--------------------------------------------
--------------------------------------------Created by Shepard Gordon-------------------------------------------
#Overview
Within the discipline of geology, there is a traditional inclination to view and sort geological information primarily through location. Geologists will often begin testing and researching by sorting their sites by geography(i.e all sites in sub-Saharan Africa or all sites in upstate New York), then narrowing by other factors such as period or lithology. By taking an information technology approach to site information by utilizing database storage and querying, geologists would be able to sort and visualize information by any attribute/sub-attribute with or without any geography limiting results (i.e. querying all geological sites with sandstone in the world or all geological sites from the Jurassic period in China). To achieve this perspective shift, the "Surface Geology Reader" or "SGR" project was developed to allow users to input a ARCGIS GeoJson file, load in polygons to a database, search any number of combinations of attributes and sub-attributes, then generate a map to visualize the searches. To achieve this, the SGR requires a user interface on a website any user can search, query and visualize data without needing to write code. The SGR project was developed principally to be used by geologists for the United States Geological Survey agency, while also potentially being available as an educational tool in the future.
#Prerequisites
Python (Minimum of 2.6 required for parsing JSON file with “.loads” function. Tested with Python 3.6)
Flask (Tested with version 0.12.2)
Redis(Tested with version 2.4.6)
PyRedis
#Installing and Setup#
Step One - Download all files in the repository FlaskApp file
Step Two - Ensure all prerequisites are loaded , and a Redis database is running available for local port 6379
Step Three - Open up a command prompt window and navigate to the installed FlaskApp folder.
Step Four - Type in command “python run.py” to start the Flask application
Step Five - Application is now ready for use at default server address 127.0.0.1:5000
#Running#
Step One - Begin by submitting a GEOJSON file. This will load all the data into a redis database. Loading may take several minutes!
Step Two - Select an attribute from the attribute box. If the attribute has less than 100 unique sub-attributes a sub-attribute box will appear. Alternatively you can submit a sub-attribute using the input box. Press submit to query the attribute and sub-attribute 
Step Three-When ready to visualize your data, press the submit map
#Known Issues#
Clicking on an attribute in the attribute box with less than 100 unique sub-attributes will cause the appropriate sub-attribute box to appear. Clicking on another attribute does not cause the old sub-attribute box to disappear
At a certain point loading too many polygons to the Google Map (approximately 10,000+) will cause the browser to run out of memory and crash

