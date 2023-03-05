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
session.commit()
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
        f"/api/v1.0/<start> and<br/>"
        f"/api/v1.0/<end><br/>"
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
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    DPscores = session.query(Measurement.date, Measurement.prcp).filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date).order_by(Measurement.date).all()
    session.close()
    return jsonify(dict(DPscores))

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # maxD = session.query(func.max(Measurement.date)).first()
    # query_date = (str(dt.datetime.strptime(maxD[0], '%Y-%m-%d') - dt.timedelta(days=365)))[:10]
    # Perform a query to retrieve the data and precipitation scores
    DPtobs = session.query(Measurement.date, Measurement.tobs).filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date).filter(Measurement.station == 'USC00519281').all()
    session.close()
    Ltobs = []
    for prcp in DPtobs:
        Ltobs_dict={}
        Ltobs_dict['tobs'] = tobs
        Ltobs.append(Ltobs_dict)
    return jsonify(dict(DPtobs))

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
        Measurement_dict["prcp"] = prcp
        Measurement_dict["tobs"] = tobs
        all_Measurements.append(Measurement_dict)

    return jsonify(all_Measurements)


if __name__ == '__main__':
    app.run(debug=True)
