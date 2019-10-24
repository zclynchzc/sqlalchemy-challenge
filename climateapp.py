from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

def calc_temps(start_date, end_date):
    session = Session(engine)
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Climate App Home Page<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_entry_prcp = session.query(Measurement.date).order_by(Measurement.date.desc()).all()[0][0]
    last_year_prcp = dt.datetime.strptime(last_entry_prcp, '%Y-%m-%d') - dt.timedelta(days=365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year_prcp).filter(Measurement.prcp >= 0).order_by(Measurement.date).all()
    
    dateprcp_list = []
    prcp_list = []
    for x in prcp_data:
        dateprcp_list.append(x[0])
        prcp_list.append(x[1])
    return jsonify(dict(zip(dateprcp_list, prcp_list)))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = []
    for y in session.query(Measurement.station).distinct().all():
        station_list.append(y[0])
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_entry_tobs = session.query(Measurement.date).order_by(Measurement.date.desc()).all()[0][0]
    last_year_tobs = dt.datetime.strptime(last_entry_tobs, '%Y-%m-%d') - dt.timedelta(days=365)
    temp_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year_tobs).order_by(Measurement.date).all()
    
    datetobs_list = []
    temp_list = []
    for x in temp_data:
        datetobs_list.append(x[0])
        temp_list.append(x[1])
    return jsonify(dict(zip(datetobs_list, temp_list)))

@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session(engine)
    last_entry_start = session.query(Measurement.date).order_by(Measurement.date.desc()).all()[0][0]
    start_data = calc_temps(start, last_entry_start)
    return jsonify(start_data)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    startend_data = calc_temps(start, end)
    return jsonify(startend_data)

if __name__ == "__main__":
    app.run(debug=True)