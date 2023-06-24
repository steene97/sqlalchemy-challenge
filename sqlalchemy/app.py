import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


##################
# Database Setup
###################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

##############
# Flask Setup
################
app = Flask(__name__)


################
# Flask Routes
################

@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Welcome to our site! We offer free highly specialised weather APIs on Hawaii - no signup required! :)<br/>"
        f"<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"   - Format: JSON. Precipitation levels (in inches) by date for 12 months from 2016-08-23<br/>"
        f"<br/>"
        f"/api/v1.0/stations</br>"
        f"   - Format: JSON. List of weather stations<br/>"
        f"<br/>"        
        f"/api/v1.0/tobs</br>"
        f"   - Format: JSON. List of temperature observations (TOBS) (in fahrenheit) for the most active station for 12 months from 2016-08-23<br/>" 
        f"<br/>"
        f"/api/v1.0/&lt;start&gt;</br>"
        f"   - Input start date in YYYY-MM-DD<br/>"
        f"   - Format: JSON. List of minimum temperature, average temperature and maximum temperature from a given period<br/>"
        f"<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;</br>"
        f"   - Input start date and end date in YYYY-MM-DD<br/>"
        f"   - Format: JSON. List of minimum temperature, average temperature and maximum temperature between the given start and end dates (inclusive)<br/>"
    )


# Input results into variables from our analysis from the Jupyter Notebook for our routes below
last_update = "2017-08-23"
year_ago = "2016-08-23"
most_active_station = "USC00519281"


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all dates and precipitation values"""   

    # Query all precipitation by date
    results = session.query(Measurement.date, Measurement.prcp)\
                .filter(Measurement.date >= year_ago)\
                .group_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for row in results:
        precipitation_dict = {}
        precipitation_dict[row.date] = row.prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations from the dataset"""
    # Query all passengers
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations by date from the most active station for 12 months"""
    # Query all tobs within last 12 months by date for station with highest observation
    results = session.query(Measurement.date, Measurement.tobs)\
            .filter(Measurement.station == most_active_station)\
            .filter(Measurement.date >= year_ago)\
            .all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Station"] = most_active_station
        tobs_dict["Date"] = date
        tobs_dict["Total Observations"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of minimum temperature, average temperature and maximum temperature from a given period"""
    # Query all tobs from the given period and calculate the min, avg and max temperatures
    results = session.query(func.min(Measurement.tobs)\
                            ,func.max(Measurement.tobs)\
                            ,func.avg(Measurement.tobs))\
                            .filter(Measurement.date >= start).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_temp_calc
    all_temp_calc = []
    for tmin, tavg, tmax in results:
        temp_calc_dict = {}
        temp_calc_dict["Start Date"] = start
        temp_calc_dict["Last Date"] = last_update
        temp_calc_dict["Minimum Temperature"] = tmin
        temp_calc_dict["Average Temperature"] = tavg
        temp_calc_dict["Maximum Temperature"] = tmax
        all_temp_calc.append(temp_calc_dict)

    return jsonify(all_temp_calc)


@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of minimum temperature, average temperature and maximum temperature between the given start and end dates (inclusive)"""
    # Query all tobs from the given periods and calculate the min, avg and max temperatures
    results = session.query(func.min(Measurement.tobs)\
                            ,func.max(Measurement.tobs)\
                            ,func.avg(Measurement.tobs))\
                            .filter(Measurement.date >= start, Measurement.date <= end)\
                            .all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_temp_calcs
    all_temp_calcs = []
    for tmin, tavg, tmax in results:
        temp_calc_dicts = {}
        temp_calc_dicts["Start Date"] = start
        temp_calc_dicts["End Date"] = end
        temp_calc_dicts["Minimum Temperature"] = tmin
        temp_calc_dicts["Average Temperature"] = tavg
        temp_calc_dicts["Maximum Temperature"] = tmax
        all_temp_calcs.append(temp_calc_dicts)

    return jsonify(all_temp_calcs)


if __name__ == '__main__':
    app.run(debug=False)
