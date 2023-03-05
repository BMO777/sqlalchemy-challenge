import numpy as np
import datetime as dt

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
Base.prepare(autoload_with=engine)

# # Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#date retreival

session = Session(engine)
maxD = session.query(func.max(Measurement.date)).first()
query_date = (str(dt.datetime.strptime(maxD[0], '%Y-%m-%d') - dt.timedelta(days=365)))[:10]
session.close()


LHA = [Measurement.date, 
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs),]
# Date_list = session.query(Measurement.date).order_by(Measurement.date).all()
################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes to find a place to soak in the sun."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/percitpitation'>/api/v1.0/percitpitation</a></br>"
        f"/api/v1.0/stations<br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></br>"
        f"/api/v1.0/2017-08-17 and<br/>"
        f"/api/v1.0/2017-07-17/2017-08-17"
    )


@app.route("/api/v1.0/stations")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Station names"""
    # Query all Stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)


@app.route("/api/v1.0/percitpitation")
def percitpitation():
    
    session = Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    DPscores = session.query(Measurement.date, Measurement.prcp).filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date).order_by(Measurement.date).all()
    session.close()
    return jsonify(dict(DPscores))

@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)
    DPtobs = session.query(Measurement.date, Measurement.tobs).filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date).filter(Measurement.station == 'USC00519281').all()
    session.close()
    Ltobs = []
    for date, tobs in DPtobs:
        Measurement_dict = {}
        Measurement_dict["Temperature"] = tobs
        Ltobs.append(Measurement_dict)
    return jsonify(Ltobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Fetch the date which matches
       the path variable supplied by the user, or a 404 if not."""
    try:

        session = Session(engine)
        search_return = session.query(*LHA).filter(func.strftime('%Y-%m-%d', Measurement.date) >= f'{start}').group_by(Measurement.date).all()
        session.close()
        LHAsearch = []
        for date, min, max, avg in search_return:
            Measurement_dict = {}
            Measurement_dict["date"] = date
            Measurement_dict["min"] = min
            Measurement_dict["max"] = max
            Measurement_dict["avg"] = avg
            LHAsearch.append(Measurement_dict)
        return jsonify((LHAsearch))
    except Exception as e:
        return jsonify({"error": f"Date '{start}' not found."}), 404

@app.route("/api/v1.0/<start>/<end>")
def startend_date(start, end):
    """Fetch the date which matches
       the path variable supplied by the user, or a 404 if not."""
    try:

        session = Session(engine)
        search_return = session.query(*LHA).filter(func.strftime('%Y-%m-%d', Measurement.date) >= f'{start}',(func.strftime('%Y-%m-%d', Measurement.date)  <= f'{end}')).group_by(Measurement.date).all()
        session.close()
        LHAsearch = []
        for date, min, max, avg in search_return:
            Measurement_dict = {}
            Measurement_dict["date"] = date
            Measurement_dict["min"] = min
            Measurement_dict["max"] = max
            Measurement_dict["avg"] = avg
            LHAsearch.append(Measurement_dict)
        return jsonify((LHAsearch))
    except Exception as e:
        return jsonify({"error": f"Date range {start} - {end} not found."}), 404


@app.route("/api/v1.0/Measurements")
def Measurements():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of Measurement data including the date, prcp, and tobs of each Measurement"""
    # Query all Measurements
    results = session.query(Measurement.date, Measurement.prcp, Measurement.tobs).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_Measurements
    all_Measurements = []
    for date, prcp, tobs in results:
        Measurement_dict = {}
        Measurement_dict["date"] = date
        # Measurement_dict["prcp"] = prcp
        # Measurement_dict["tobs"] = tobs
        all_Measurements.append(Measurement_dict)

    return jsonify(all_Measurements)

if __name__ == '__main__':
    app.run(debug=True)
