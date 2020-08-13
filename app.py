#import dependencies 
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime

#database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)
#save reference to tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#create app
app = Flask(__name__)

#FLask routes
@app.route("/")
def home():
    print("Server received request for 'home' page")
    return (
        f"Welcome to the Climate App API: <br/>"
        f'Please see available routes:<br/>'
        f'Precipitation route to view date and documented rainfall:<br/>'
        f'/api/v1.0/precipitation <br/>'
        f'Station route to view list of documented stations:<br/>'
        f'/api/v1.0/stations <br/>'
        f'Tobs route to view summary data for 2016-2017 year and raw data points:<br/>'
        f'/api/v1.0/tobs <br/><br/>'
        f"Search for a specific start date (start/YYYY-MM-DD) <br/>"
        f'/api/v1.0/date/start/<start> <br/>'
        f"Serarch for a specific date range between a start/end date by entering (start/YYYY-MM-DD/end/YYYY-MM-DD)<br/>"
        f'/api/v1.0/date/start/<start>/end/<end> <br/>'
    )

@app.route("/api/v1.0/precipitation")
def percipitation():
    #create session link from Python to the DB
    session = Session(engine)
    """Return Precipitation data as json"""
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
                        order_by(Measurement.date).all()
    session.close()
    #convert list into normal list
    all_precipitation = []
    for date, prcp in prcp_results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["precipitation"] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():  #create session link from Python to the DB
    session = Session(engine)
    """Return Station data as json"""
    station_results = session.query(Station.station,Station.name).all()
    session.close()
    #convert list into normal list
    all_stations = []
    for station, name in station_results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Details"] = name
        all_stations.append(station_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """Return Temp data as json"""
    temp_min_max_avg = {
        Measurement.station,
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)}

    temp_results = session.query(*temp_min_max_avg).filter(Measurement.station == "USC00519281").all()
    last_temps = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= '2016-08-23').filter(Measurement.date <= '2017-08-23').all()
    session.close()
    #convert list into normal list
    calc_temps = []
    for station, min, max, avg in temp_results:
        calc_dict ={}
        calc_dict["Station"] = station
        calc_dict["Min"] = min
        calc_dict["Max"] = max
        calc_dict["Average"] = avg
        calc_temps.append(calc_dict)

    temps = []
    for date, station, tobs in last_temps:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Station"] = station
        temp_dict["Rainfall"] = tobs
        temps.append(temp_dict)
    return jsonify(calc_temps, temps)


@app.route("/api/v1.0/date/start/<start>", methods=['GET'])
def start(start):
    """When given the start only, calculate TMIN, TAVG, and TMAX 
    for all dates greater than and equal to the start date"""
    session = Session(engine)
    #This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
        """
    
    start_results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d",Measurement.date >= start)).group_by(Measurement.date).all() 
    session.close()

    all_start_date = []
    for date, min, avg, max in start_results:
        start_date_dict = {}
        start_date_dict["date"] = date
        start_date_dict["min"] = min
        start_date_dict["avg"] = avg
        start_date_dict["max"] = max
        all_start_date.append(start_date_dict)
    return jsonify(all_start_date)


@app.route("/api/v1.0/date/start/<start>/end/<end>",methods=['GET'])
def date(start,end):
    """When given the start only, calculate TMIN, TAVG, and TMAX 
    for all dates greater than and equal to the start date"""
    session = Session(engine)

    #This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    start_end_results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d",Measurement.date >= start)).filter(func.strftime("%Y-%m-%d",Measurement.date <= end)).group_by(Measurement.date).all() 
    session.close()

    all_start_end_date = []
    for date, min, avg, max in start_end_results:
        start_end_date_dict = {}
        start_end_date_dict["date"] = date
        start_end_date_dict["min"] = min
        start_end_date_dict["avg"] = avg
        start_end_date_dict["max"] = max
        all_start_end_date.append(start_end_date_dict)
    return jsonify(all_start_end_date)

if __name__ == "__main__":
    app.run(debug=True)
