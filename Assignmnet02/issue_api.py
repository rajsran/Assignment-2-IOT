from flask import Flask, Blueprint, request, jsonify, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os, requests, json
from flask import current_app as app
from car_api import Car, capi, cdb
from add_event import CalendarEvent

from datetime import datetime
from datetime import timedelta

iapi = Blueprint("iapi", __name__)

idb = SQLAlchemy()
ima = Marshmallow()

# Declaring the model.
class Issue(idb.Model):
    __tablename__ = "Issue"
    reportID = idb.Column(idb.String(50), primary_key = True)
    carnumber = idb.Column(idb.String(6), nullable = False)
    reportedBy = idb.Column(idb.String(200), nullable = False)
    solvedBy = idb.Column(idb.String(200))
    reportedOn = idb.Column(idb.Date, nullable=False)
    closedOn = idb.Column(idb.Date)
    isOpen = idb.Column(idb.Boolean, default=True)
    '''
    def addToCalendar(self, service):
        cal = CalendarEvent(self.start_date, self.booking_id, self.start_location)
        eid = cal.addToCalendar(self.carnumber, service)
        return eid
 
    def removeFromCalendar(self, service):
        cal = CalendarEvent(self.start_date, self.booking_id, self.start_location)
        cal.removeFromCalendar(self.event_id, service)
     '''   
class IssueSchema(ima.Schema):
    # Reference: https://github.com/marshmallow-code/marshmallow/issues/377#issuecomment-261628415
    def __init__(self, strict = True, **kwargs):
        super().__init__(strict = strict, **kwargs)
    
    class Meta:
        # Fields to expose.
        fields = ("reportID", "reportedOn", "reportedBy", "solvedBy", "isOpen", "closedOn", "carnumber")

issueSchema = IssueSchema()
issuesSchema = IssueSchema(many = True)

# Endpoint to show all bookings.
@iapi.route("/issue", methods = ["GET"])
def getIssue():
    issues = Issue.query.all()
    result = issuesSchema.dump(issues)

    return jsonify(result.data)
