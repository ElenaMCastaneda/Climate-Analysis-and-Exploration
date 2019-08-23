import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List to all the available routes."""
    return (
        f"~ CLIMATE API PAGE ~<br/>" 
        "<br/>"
        f"Below is a list of all the available routes:<br/>"
         "<br/>"      
        f"*/api/v1.0/precipitation<br/>"
          "<br/>"
        f"*/api/v1.0/stations<br/>"
          "<br/>"
        f"*/api/v1.0/tobs<br/>"
          "<br/>"
        f"*/api/v1.0/2017-08-20<br/>"
          "<br/>"
        f"*/api/v1.0/2017-08-20/2017-08-23<end>"
 )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """ Convert the query results to a Dictionary using `date` as the key and `prcp` as the value """
    session = Session(engine)
    data_points = session.query(Measurement.date, Measurement.prcp).all()
        
    # Create a dictionary
    prcp_data = []
    for date, prcp in data_points:
       prcp_dict = {}
       prcp_dict["date"] = date
       prcp_dict["prcp"] = prcp
       prcp_data.append(prcp_dict)
  
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    
    # Query all stations
    session = Session(engine)
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point."""
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    #from datetime import timedelta
    last_date = dt.date(2017,8,23)
    year = dt.timedelta(days=365)
    query_date = last_date - year
   
    # Query all tobs values
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.date == query_date).all()

    # Convert list of tuples into normal list
    tobs_values = list(np.ravel(results))

    return jsonify(tobs_values)

@app.route("/api/v1.0/<start>")
def temperatures_start(start):
    """ Given the start only, calculate TMIN, TAVG, & TMAX for all dates greater than and equal to the start date.     """
    session = Session(engine)
    results = session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
 
    temperatures_start = list(results)
    return jsonify(temperatures_start)

app.route("/api/v1.0/<start>/<end>")
def temperatures_start(start, end):
    """ When given the start & end dates, calculate `TMIN`, `TAVG`, & `TMAX` for dates between the start and end date"""
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
   

    # Convert list of tuples into normal list
    query_results = list(np.ravel(results))
    return jsonify(query_results)

if __name__ == "__main__":

    app.run(debug=True)