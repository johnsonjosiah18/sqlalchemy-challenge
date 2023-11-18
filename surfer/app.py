# Import dependencies
import sqlalchemy
import pandas as pd
import numpy as np
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

# Set up database engine for flask app
# Create function that allows access to SQLite database file
dataloc = "../Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{dataloc}")

# Reflect databases into classes
Base = automap_base()

# Reflect tables
Base.prepare(engine, reflect=True)

# Set class variables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Creates session link from Python to SQLite database
session = Session(engine)

# Create Flask app, all routes go after this code
app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
 
    # Calculate the date one year from the last date in data set
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():

    # Query all Stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the last year of data.
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station = most_active_station[0]

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active_station).\
    filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    tobs_data = {date: tobs for date, tobs in results}

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
    # Query TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    # Convert the query results to a dictionary
    temp_data = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Query TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert the query results to a dictionary
    temp_data = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}

    return jsonify(temp_data)
    




if __name__ == '__main__':
    app.run(debug=True)