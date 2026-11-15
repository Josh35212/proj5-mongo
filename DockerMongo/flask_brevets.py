"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY
client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
db = client.brevets


###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")

    km = request.args.get('km', type=float)
    distance = request.args.get("distance", type=int)
    begin_date = request.args.get("begin_date")
    begin_time = request.args.get("begin_time")

    app.logger.debug("km={}".format(km))
    app.logger.debug("distance={}".format(distance))
    app.logger.debug("begin_date={}".format(begin_date))
    app.logger.debug("begin_time={}".format(begin_time))
    app.logger.debug("request.args: {}".format(request.args))

    # Handles errors
    try:
        start_time = "{}T{}".format(begin_date, begin_time)
        open_time = acp_times.open_time(km, distance, start_time)
        close_time = acp_times.close_time(km, distance, start_time)
    except (ValueError, TypeError, arrow.parser.ParserError):
        return flask.jsonify(erro="Invalid Input"), 400

    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route("/insert", methods=["POST"])
def insert():
    controls = request.get_json(silent=True)

    # Error handles for invalid or empty inputs
    if not isinstance(controls, list) or not controls:
        return flask.jsonify(error="Invalid control list"), 400
    for control in controls:
        if not isinstance(control, dict): 
            return flask.jsonify(error="Each control must be an object"), 400
        # Check if all the keys exist
        if not all(field in control for field in ("km", "open", "close")):
            return flask.jsonify(error="Missing required control fields"), 400
        # Check if all the keys have a value
        if not all(control[field] not in (None, "") for field in ("km", "open", "close")):
            return flask.jsonify(error="Missing required control values"), 400

    try:    
        db.times.insert_many(controls)
    except PyMongoError:
        app.logger.exception("Unable to save control times")
        return flask.jsonify(error="Unable to save control times"), 500
    
    return flask.jsonify(status="ok")

@app.route("/fetch", methods=["GET"])
def fetch():
    try:
        times = list(db.times.find({}, {"_id": 0}))
    except PyMongoError:
        app.logger.exception("Unable to fetch stored control times")
        return flask.jsonify(error="Unable to fetch stored control times"), 500
    
    return flask.jsonify(times=times)

@app.route("/display")
def display():
    return flask.render_template("display.html")

#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
