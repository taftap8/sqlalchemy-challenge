#import dependencies 
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

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
        f'/api/v1.0/precipitation <br/>'
        f'/api/v1.0/stations <br/>'
        f'/api/v1.0/tobs <br/>'
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
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():  #create session link from Python to the DB
    session = Session(engine)
    """Return Station data as json"""
    station_results = session.query(Station.station).all()
    session.close()
    #convert list into normal list
    all_stations = list(np.ravel(station_results))
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
    session.close()
    #convert list into normal list
    all_temps = list(np.ravel(temp_results))
    return jsonify(all_temps)

if __name__ == "__main__":
    app.run(debug=True)
