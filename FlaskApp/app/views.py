#Import all flask operations needed
from flask import render_template, flash, session, request, jsonify
from flask.sessions import SessionInterface
#Import redis to use as a database
import redis
from app import app
#Imported to read inital json file
import json
#Imported for math.floor
import math

import sys

#Setup the databases we will use
attributes = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
page_usage = redis.StrictRedis(host='localhost', port=6379, db=1, charset="utf-8", decode_responses=True)
search_terms = redis.StrictRedis(host='localhost', port=6379, db=2, charset="utf-8", decode_responses=True)
geology_hash = redis.StrictRedis(host='localhost', port=6379, db=3, charset="utf-8", decode_responses=True)
query_values = redis.StrictRedis(host='localhost', port=6379, db=4, charset="utf-8", decode_responses=True)

#Setup the inital page we will use
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', attribute_list= [], toggle= False, times = 0, total_polygons= 0, current_polygons = 0, attribute_tuples = [], search_terms = search_terms)

#Inital reading of the file
@app.route("/file_input/", methods=['POST'])
def file_input():
    #Since we are getting a new file, clear out the old information from our datatbases
    attributes.flushdb()
    page_usage.flushdb()
    search_terms.flushdb()
    geology_hash.flushdb()
    query_values.flushdb()
    #If a file is not given, throw an error message
    if(request.form.get("datafile") == ""):
        return("Error, no file is selected")
    else:
        page_usage.set('input_file', request.form.get("datafile"))
    attribute_list = []
    #Go through the list of all possible field types and add them to the list	
    with app.open_resource(page_usage.get("input_file")) as f:
	    full_line = f.read()
	    #Requires Python 3.6
	    all_data = json.loads(full_line)
    page_usage.set('original_polygons', len(all_data["features"]))
    sub_attributes = []
    #Go through the list of all possible field types and add them to the list
    count=0
    for x in range(0, int(page_usage.get('original_polygons'))):
        for attribute in all_data["features"][0]["properties"]:
            sub_attribute = str(all_data["features"][x]["properties"][attribute])
            geology_hash.hset(x, attribute, sub_attribute)
            attributes.sadd(attribute, sub_attribute)
        geology_hash.hset(x, "COORDINATES", str(all_data["features"][x]["geometry"]["coordinates"]))
        query_values.sadd('final_values', x)
        query_values.sadd('all_values', x)
        print(count)
        count+=1
    #print(str(query_values.sinter('final_values')))
    print("Hash done")  
	    
    #Set the total attributes/sub-attributes searched to zero
    page_usage.set('times', 0)
    return render_template('index.html', toggle= True, times = page_usage.get('times'), total_polygons = page_usage.get('original_polygons'), current_polygons = str(len(query_values.sinter('final_values'))), attributes = attributes, search_terms = search_terms)

@app.route("/sort/", methods= ['POST'])
def load_sub_attributes():
    attribute = request.form.get("attribute")
    if(request.form.get("submit_sub_attribute_text") != ""):
        sub_attribute = request.form.get("submit_sub_attribute_text")
    else:
        sub_attribute = request.form.get(attribute)
    search_terms.set(attribute, sub_attribute)
    for x in geology_hash.keys():
        if str(sub_attribute) != str(geology_hash.hget(x, attribute)):
                query_values.srem('final_values', x)
    page_usage.incr('times')
    return render_template('index.html', toggle= True, times = page_usage.get('times'), total_polygons = page_usage.get('original_polygons'), current_polygons = str(len(query_values.sinter('final_values'))), attributes = attributes, search_terms = search_terms)

#Prints the map
@app.route("/generate_map/", methods=['POST'])
def map():
    geology_dict = {}
    #Loads all polygons with only the requested features included
    for x in query_values.sinter('final_values'):
	    geology_dict[x] = {}
	    for attribute in search_terms.keys():
		    geology_dict[x][attribute] = geology_hash.hget(x, attribute)
	    #Manually add these every time	
	    geology_dict[x]["ERA"] = geology_hash.hget(x, "ERA")
	    geology_dict[x]["PERIOD"] = geology_hash.hget(x, "PERIOD")
	    geology_dict[x]["LITHOLOGY"] = geology_hash.hget(x, "LITHOLOGY")
	    geology_dict[x]["ROCK_CLASS"] = geology_hash.hget(x, "ROCK_CLASS")
	    geology_dict[x]["ROCK_SUBCL"] = geology_hash.hget(x, "ROCK_SUBCL")
	    geology_dict[x]["CHEMISTRY"] = geology_hash.hget(x, "CHEMISTRY")
	    #Add in coordinates
	    coordinate_pair = geology_hash.hget(x, "COORDINATES")
	    all_coordinates = str(coordinate_pair).replace("[","").replace("]","")
	    all_coordinates = all_coordinates.split(",")
	    count = 0
	    geology_dict[x]["coordinates"] = []
	    while(count < len(all_coordinates)):
                geology_dict[x]["coordinates"].append(tuple((float(all_coordinates[count]), float(all_coordinates[count+1]))))
                count+=2
	    #return(str(geology_dict[x]["coordinates"]))
	    #geology_dict[x]["coordinates"] = []
	    #for pair in coordinate_pair[0]:
		    #new_pair = tuple(pair)
		    #geology_dict[x]["coordinates"].append(new_pair)
	    
    #return(str(request.form.get("color")))
    color_option = request.form.get("color")
    
    
    #Return the length of our current dictionary
    return render_template('map_final.html', toggle= True, times = page_usage.get('times'), total_polygons = page_usage.get('original_polygons'), current_polygons = str(len(query_values.sinter('final_values'))), attributes = attributes, search_terms = search_terms, geology_dict= geology_dict, color_option = color_option)


@app.route("/reset/", methods=['POST'])
def reset():
    #Reset the number of times we have searched and clear the search term database
    page_usage.set('times', 0)
    query_values.delete('final_values')
    for val in query_values.sinter('all_values'):
        query_values.sadd('final_values', val)	
    search_terms.flushdb()
    
    return render_template('index.html', attribute_list= sorted(list(attributes.keys())), toggle = True, attributes = attributes, times = 0, total_polygons = page_usage.get('original_polygons'), current_polygons = str(len(query_values.sinter('final_values'))), search_terms = search_terms)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'