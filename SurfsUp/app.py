# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
#Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("These are the available routes")
    return (
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the data set.
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    # Calculate the date one year from the last date in data set.
    most_recent_date = dt.datetime.strptime(most_recent, '%Y-%m-%d').date()
    starting_date = most_recent_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= starting_date).\
            filter(Measurement.date <= most_recent_date).all()

    session.close()

    # Convert query to a dictionary
    precipitation_dict = {}
    for result in results:
        date = result[0]
        prcp = result[1]
        precipitation_dict[date] = prcp

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all stations
    results = session.query(Station.station, Station.name).all()
    
    session.close()

    # Convert query to a list of dictionaries
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # List the stations and their counts in descending order.
    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(desc(func.count(Measurement.station))).all()

    # Calculate most recent date for specific station
    most_recent_active_station = session.query(Measurement.date).\
                            filter(Measurement.station==station_activity[0][0]).\
                            order_by(Measurement.date.desc()).first()[0]

    # Convert date string to date object and calculate starting date
    most_recent_date_active_station = dt.datetime.strptime(most_recent_active_station,'%Y-%m-%d').date()
    starting_date_active_station = most_recent_date_active_station - dt.timedelta(days=365)

    # Query to retrieve data
    last_twelve_months_query = session.query(Measurement.date, Measurement.tobs).\
                            filter(Measurement.station==station_activity[0][0]).\
                            filter(Measurement.date >= starting_date_active_station).\
                            filter(Measurement.date <= most_recent_date_active_station).all()

    
    session.close()

    # Convert query to a dictionary
    tobs_dict = {}
    for result in last_twelve_months_query:
        date = result[0]
        tobs = result[1]
        tobs_dict[date] = tobs

    return jsonify(tobs_dict)


@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to retrieve aggregates
    results = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    session.close()

    # Convert query to list of dicts
    all_temps = []
    for tmin, tavg, tmax in results:
        temp_dict = {}
        temp_dict["TMIN"] = tmin
        temp_dict["TAVG"] = tavg
        temp_dict["TMAX"] = tmax
        all_temps.append(temp_dict)

    return jsonify(all_temps)


@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to retrieve aggregates
    results = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

    session.close()

    # Convert query to list of dicts
    all_temps = []
    for tmin, tavg, tmax in results:
        temp_dict = {}
        temp_dict["TMIN"] = tmin
        temp_dict["TAVG"] = tavg
        temp_dict["TMAX"] = tmax
        all_temps.append(temp_dict)

    return jsonify(all_temps)


if __name__ == "__main__":
    app.run(debug=True)