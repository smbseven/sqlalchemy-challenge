#NAME: SQL-Alchemy Challenge
#PURPOSE:  Flask API based on queries
#Dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

#Database & Reference setup

#DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()
Base = automap_base()
Base.prepare(engine, reflect=True)

#References
h_measure = Base.classes.measurement
h_station = Base.classes.station

#Flask setup
app = Flask(__name__)

#FLASK ROUTES

#Flask Routes (home)
@app.route("/")
def home():
    """Show available api routes."""
    return f"""
        <p>Available Routes:</p>
        <p>/api/v1.0/precipitation</p>
        <p>/api/v1.0/stations</p>
        <p>/api/v1.0/tobs</p>
        <p>/api/v1.0/&lt;start&gt;</p>
        <p>/api/v1.0/&lt;start&gt;/&lt;end&gt;</p>
    """
#Flask Routes (precipitation)
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session
    session = Session(engine)

    # Query dates and precipitation values
    pre_s = session.query(h_measure.date,h_measure.prcp).order_by(h_measure.date).all()
    # Add results from query to date and precipitation lists
    dates = [row[0] for row in pre_s]
    prcp = [row[1] for row in pre_s]
    # Create dictionary to present data in json format
    zip_iter = zip(dates, prcp)
    prcp_dict = dict(zip_iter)

    # Close session
    session.close()

    # JSON Response
    return jsonify(prcp_dict)


#Flask Routes (stations)
@app.route("/api/v1.0/stations")
def stations():
    # Create session
    session = Session(engine)

    # Query station values
    stat = session.query(h_station.station, h_station.name).all()
    # Create list to get results
    stations = {}
    for s,name in stat:
        stations[s] = name
    # Close session
    session.close()
 
     # JSON Response
    return jsonify(stations)

#Flask Routes (date/station/tobs)
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session
    session = Session(engine)

    # Get last date in db
    l_d_q = session.query(h_measure.date).order_by(h_measure.date.desc()).first()

    #Date calculation - automate calculation of 1 year prior to last date
    l_y_d = (dt.datetime.strptime(l_d_q[0],'%Y-%m-%d') \
                    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query for corresponding dates and temperature values for most active station
    l_h_t = session.query(h_measure.date,h_measure.tobs).filter(h_measure.station == 'USC00519281', h_measure.date>=l_y_d).all()

    #Add results from query to lists
    q_dates = [row[0] for row in l_h_t]
    q_tobs = [row[1] for row in l_h_t]
    # Create dictionary to present data in json format
    zip_iter_tobs = zip(q_dates, q_tobs)
    tobs_dict = dict(zip_iter_tobs)

    # Close session
    session.close()

    # JSON Response
    return jsonify(tobs_dict)
    
#Flask Routes function start date
#Function definition
@app.route("/api/v1.0/<start>")
def t_r_s(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create session
    session = Session(engine)

    #Query for start date after user input @ broswer
    st_query = session.query(h_measure.date,func.min(h_measure.tobs),func.avg(h_measure.tobs),func.max(h_measure.tobs)).filter(h_measure.date >= start).group_by(h_measure.date).all()
    
    #Structure response to present data
    st_l = []

    for date, min, avg, max in st_query:
        st_dict = {}
        st_dict["Date"] = date
        st_dict["TMIN"] = min
        st_dict["TAVG"] = avg
        st_dict["TMAX"] = max
        st_l.append(st_dict)

    session.close()    

    return jsonify(st_l)

#Flask Routes function start date - end date
#Function definition
@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    """TMIN, TAVG, and TMAX per date for a date range.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query for start and end date after user input @ broswer
    s_e_query = session.query(h_measure.date,func.min(h_measure.tobs), func.avg(h_measure.tobs), func.max(h_measure.tobs)).filter(h_measure.date >= start, h_measure.date <= end).group_by(h_measure.date).all()

    #Structure response to present data
    st_en_l = []

    for date, min, avg, max in s_e_query:
        s_e_d = {}
        s_e_d["Date"] = date
        s_e_d["TMIN"] = min
        s_e_d["TAVG"] = avg
        s_e_d["TMAX"] = max
        st_en_l.append(s_e_d)

    session.close()    

    return jsonify(st_en_l)

if __name__ == '__main__':
    app.run(debug=True)