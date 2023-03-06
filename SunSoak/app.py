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

#lowest highest average temps calculation variable
LHA = [Measurement.date, 
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs),]

################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes"""
    return (
        f" Welsome, hope this api helps you find a place to soak in the sun.<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></br>"
        f"<a href= '/api/v1.0/stations'>/api/v1.0/stations</a></br>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></br>"
        f"/api/v1.0/2017-08-17 and<br/>"
        f"/api/v1.0/2017-07-17/2017-08-17"
    )


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Station columns"""
    # Query all Stations
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()
    Slist = []
    for id, sta, name, lat, lng, ele in results:
        Station_dict = {}
        Station_dict["id"] = id
        Station_dict["station"] = sta
        Station_dict["name"] = name
        Station_dict["latitude"] = lat
        Station_dict["longitude"] = lng
        Station_dict["elevation"] = ele
        Slist.append(Station_dict)
    # Convert list of tuples into normal list
    # stations = list(np.ravel(results))

    return jsonify(Slist)


@app.route("/api/v1.0/precipitation")
def percitpitation():
    
    session = Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    DPscores = session.query(Measurement.date, Measurement.prcp).filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date).all()
    session.close()
    return jsonify(dict(DPscores))

@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)
    DPtobs = session.query(Measurement.date, Measurement.tobs).filter(func.strftime('%Y-%m-%d', Measurement.date) >= query_date).\
        filter(Measurement.station == 'USC00519281').all()
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
        search_return = session.query(*LHA).\
            filter(func.strftime('%Y-%m-%d', Measurement.date) >= f'{start}',(func.strftime('%Y-%m-%d', Measurement.date)  <= f'{end}')).all()
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

if __name__ == '__main__':
    app.run(debug=True)
