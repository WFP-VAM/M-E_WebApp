"""
WFP Libya CO DP Manager.

Declarative–representation of all the tables in the database.
"""

from geoalchemy2 import Geometry
from extensions import db


class distribution_points2(db.Model):
    __tablename__ = 'distribution_points2'
    id = db.Column(db.Integer, primary_key=True)
    distributionpoint = db.Column(db.String(100))
    partner = db.Column(db.String(80))
    activity = db.Column(db.String(80))
    idps = db.Column(db.Boolean())
    returnees = db.Column(db.Boolean())
    nondisplaced = db.Column(db.Boolean())
    migrants = db.Column(db.Boolean())
    comments = db.Column(db.String(100))
    geom = db.Column(Geometry('POINT'))  # PostGIS data type
    mantika = db.Column(db.String(80))
    baladiya = db.Column(db.String(80))
    muhalla = db.Column(db.String(80))


class distributionfigures_gfd(db.Model):
    __tablename__ = 'distributionfigures_gfd'  # To do: rename the table distributionfigures_monthly
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, unique=False, nullable=True, primary_key=False)
    year = db.Column(db.Integer, unique=False, nullable=True, primary_key=False)
    hh_reached = db.Column(db.Integer, unique=False, nullable=True, primary_key=False)
    hh_planned = db.Column(db.Integer, unique=False, nullable=True, primary_key=False)
    distribution_point = db.Column(db.Integer, db.ForeignKey('distribution_points2.id'), nullable=False, primary_key=False)
    moomken = db.Column(db.Boolean())
    wfp = db.Column(db.Boolean())


class distributionfigures_rrm(db.Model):
    __tablename__ = 'distributionfigures_rrm'
    id = db.Column(db.Integer, primary_key=True)
    hh_reached = db.Column(db.Integer, unique=False, nullable=True, primary_key=False)
    distribution_point = db.Column(db.Integer, db.ForeignKey('distribution_points2.id'), nullable=False, primary_key=False)
    moomken = db.Column(db.Boolean())
    wfp = db.Column(db.Boolean())


class Wfp_lists(db.Model):
    __tablename__ = 'wfp_lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(80), unique=True, nullable=False)


class libya_admin2(db.Model):
    __tablename__ = 'libya_admin2'
    gid = db.Column(db.Integer, primary_key=True)
    adm2_manti = db.Column(db.String)
    geom = db.Column(Geometry('POLYGON'))


class libya_admin3(db.Model):
    __tablename__ = 'libya_admin3'
    gid = db.Column(db.Integer, primary_key=True)
    adm3_balad = db.Column(db.String)
    geom = db.Column(Geometry('POINT'))


class libya_admin4(db.Model):
    __tablename__ = 'libya_admin4'
    gid = db.Column(db.Integer, primary_key=True)
    adm4_muhal = db.Column(db.String)
    geom = db.Column(Geometry('POINT'))
