"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

# from crypt import methods
import site 

from app import app, Config,  mongo, Mqtt
from flask import escape, render_template, request, jsonify, send_file, redirect, make_response, send_from_directory 
from json import dumps, loads 
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta, timezone
from os import getcwd
from os.path import join, exists
from time import time, ctime
from math import floor
import json
 



#####################################
#   Routing for your application    #
#####################################


# 1. CREATE ROUTE FOR '/api/set/combination'
@app.route('/api/set/combination', methods=['POST'])
def insert_passcode():
    if request.method == "POST":
        try:
            form = request.form
            passcode = escape(form.get("passcode"))

            if not (passcode.isdigit() and len(passcode) == 4):
                return jsonify({"status": "failed", "data": "failed"})


            success = mongo.insertPasscode(passcode)
            if success:
                return jsonify({"status": "complete", "data": "complete"})
    
        except Exception as e:
            print(f"insert_passcode Error: f{str(e)}")
    return jsonify({"status": "failed", "data": "failed"})
    
# 2. CREATE ROUTE FOR '/api/check/combination'
@app.route('/api/check/combination', methods=['POST'])
def validate_passcode():
    if request.method == "POST":
        try:
            form = request.form
            passcode = escape(form.get("passcode"))

            if not (passcode.isdigit() and len(passcode) == 4):
                return jsonify({"status": "failed", "data": "failed"})


            success = mongo.getCount(passcode)
            if success:
                return jsonify({"status": "complete", "data": "complete"})
    
        except Exception as e:
            print(f"validate_passcode Error: f{str(e)}")
    return jsonify({"status": "failed", "data": "failed"})
    

# 3. CREATE ROUTE FOR '/api/update'
@app.route('/api/update', methods=['POST'])
def update_radar():
    if request.method == 'POST':
        try:
            data = request.get_json()
            data["timestamp"] = floor(datetime.now().timestamp())
            Mqtt.publish("620165845",mongo.dumps(data))
            Mqtt.publish("620165845_pub",mongo.dumps(data))
            Mqtt.publish("620165845_sub",mongo.dumps(data))

            print(f"MQTT: {data}")

            success=mongo.insertData(data)
            if success:
                return jsonify({"status": "complete", "data": "complete"})


        except Exception as e:   
            print(f"update_radar Error: f{str(e)}")
    return jsonify({"status": "failed", "data": "failed"})
        

   
# 4. CREATE ROUTE FOR '/api/reserve/<start>/<end>'
@app.route('/api/reserve/<start>/<end>', methods=['GET'])
def get_all_radar(start,end):
     if request.method == "GET":
        try:
            start = int(start)
            end = int(end)

            result = mongo.getAll(start,end)
            if result:
                return jsonify({"status":"success","data":result})
        except Exception as e:
            print(f"get_all_radar() error: f{str(e)}")
    
        return jsonify({"status":"failed","data":"failed"})

# 5. CREATE ROUTE FOR '/api/avg/<start>/<end>'
@app.route('/api/avg/<start>/<end>', methods=['GET'])
def average(start, end):
    if request.method == "GET":
        try:
            start = int(start)
            end = int(end)

            result = mongo.avgReserve(start,end)
            if result:
                return jsonify({"status":"success","data":result})
        except Exception as e:
            print(f"average() error: f{str(e)}")
    
        return jsonify({"status":"failed","data":"failed"})

   






@app.route('/api/file/get/<filename>', methods=['GET']) 
def get_images(filename):   
    '''Returns requested file from uploads folder'''
   
    if request.method == "GET":
        directory   = join( getcwd(), Config.UPLOADS_FOLDER) 
        filePath    = join( getcwd(), Config.UPLOADS_FOLDER, filename) 

        # RETURN FILE IF IT EXISTS IN FOLDER
        if exists(filePath):        
            return send_from_directory(directory, filename)
        
        # FILE DOES NOT EXIST
        return jsonify({"status":"file not found"}), 404


@app.route('/api/file/upload',methods=["POST"])  
def upload():
    '''Saves a file to the uploads folder'''
    
    if request.method == "POST": 
        file     = request.files['file']
        filename = secure_filename(file.filename)
        file.save(join(getcwd(),Config.UPLOADS_FOLDER , filename))
        return jsonify({"status":"File upload successful", "filename":f"{filename}" })

 


###############################################################
# The functions below should be applicable to all Flask apps. #
###############################################################


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(405)
def page_not_found(error):
    """Custom 404 page."""    
    return jsonify({"status": 404}), 404



