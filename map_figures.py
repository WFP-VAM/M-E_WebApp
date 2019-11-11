"""
WFP Libya CO DP Manager.

Flask functions to query the database and serve geojson and other parameters to a Mapbox Web Map.

To do: Combine map_figures and map_rrm as the code is very similar
"""

import datetime
from flask import render_template, request
from extensions import db, excel
from models import distribution_points2, distributionfigures_gfd, distributionfigures_rrm, Wfp_lists
from sqlalchemy import and_

from geoalchemy2 import func

from math import sqrt
from geojson import Feature, FeatureCollection
import json

today = datetime.date.today()
last_month = today - datetime.timedelta(days=30)


def map_figures(app):
    def activity2col(activity):
        """Assign coloros to activities."""
        if activity == "GFD":
            return "#2A93FC"
        elif activity == "RRM":
            return "#FF0000"
        elif activity == "School Feeding":
            return "#2AFC93"
        elif activity == "Livelihood":
            return "#FC932A"
        elif activity == "Migrants":
            return "#FC2AFC"
        else:
            return "#ff0000"

    @app.route('/', methods=['GET', 'POST'])
    def maps(month=9, year=last_month.year, select_activities=["GFD"], figure="hh_reached", aggregation="baladiya", display="circles", monitoring="all"):
        month = request.form.get("month") if request.form.get("month") else month
        year = request.form.get("year") if request.form.get("year") else year
        select_activities = request.form.getlist("activity") if request.form.getlist("activity") else select_activities
        figure = request.form.get("reached") if request.form.get("reached") else figure
        aggregation = request.form.get("aggregation") if request.form.get("aggregation") else aggregation
        monitoring = request.form.get("monitoring") if request.form.get("monitoring") else monitoring
        display = request.form.get("display") if request.form.get("display") else display
        if aggregation == "mantika":
            aggregation_list1 = ["activity", "mantika"]
        elif aggregation == "baladiya":
            aggregation_list1 = ["activity", "mantika", "baladiya"]
        elif aggregation == "distributionpoint":
            aggregation_list1 = ["activity", "mantika", "baladiya", "distributionpoint"]
        aggregation_var = aggregation_list1[-1]
        aggregation_list2 = []
        for x in aggregation_list1:
            aggregation_list2.append(getattr(distribution_points2, x))
        all_activities = Wfp_lists.query.filter_by(type="activity").all()
        query_db = query_db = db.session.query(
            distribution_points2.geom.st_union().st_centroid().ST_AsGeoJSON(),  # Taking the centroid per Baladiya
            distribution_points2.activity,
            func.min(distribution_points2.distributionpoint).label("distributionpoint"),
            func.min(distribution_points2.mantika).label("mantika"),
            func.min(distribution_points2.baladiya).label("baladiya"),
            func.bool_or(distributionfigures_gfd.moomken).label("moomken"),  # True if one is True
            func.bool_or(distributionfigures_gfd.wfp).label("wfp"),
            func.sum(getattr(distributionfigures_gfd, figure)).label("hh")).join(  # Joining disrib figures
                distributionfigures_gfd, and_(
                    distribution_points2.activity.in_(select_activities),
                    distribution_points2.id == distributionfigures_gfd.distribution_point,
                    distributionfigures_gfd.month == month,
                    distributionfigures_gfd.year == year,
                    getattr(distributionfigures_gfd, figure) > 0)).group_by(*aggregation_list2)
        response = query_db.all()
        if request.form.get("download"):
            return excel.make_response_from_query_sets(response, aggregation_list1 + ["moomken", "wfp", "hh"], "xls", file_name=month + "_" + year + "_"  +  "_".join(select_activities) + "_" + figure + ".xls")
        my_geojson = []
        total_str = "0"
        if [x.hh for x in response]:
            max_hh = max([x.hh for x in response])
            total = sum([x.hh for x in response]) * 5
            total_str = '{:,}'.format(total)
            for x in response:
                if display == "circles":
                    circle_size = sqrt(x.hh / max_hh)
                elif display == "points":
                    circle_size = 0.2
                if monitoring == "all":
                    opacity = 0.7
                elif monitoring == "wfp":
                    opacity = 0.2
                    if x.wfp is True:
                        opacity = 0.7
                elif monitoring == "moomken":
                    opacity = 0.2
                    if x.moomken is True:
                        opacity = 0.7
                feature = Feature(geometry=json.loads(x[0]),
                                  properties={
                                      "mantika": x.mantika,
                                      "baladiya": x.baladiya,
                                      "activity": x.activity,
                                      "moomken": x.moomken,
                                      "wfp": x.wfp,
                                      "distributionpoint": x.distributionpoint,
                                      "circle_size": circle_size,
                                      "circle_color": activity2col(x.activity),
                                      "circle_opacity": opacity,
                                      'ind': (x.hh) * 5,
                                      'ind_str': '{:,}'.format((x.hh) * 5)})
                my_geojson.append(feature)
        feature_collection = FeatureCollection(my_geojson)
        return render_template("map2.html",
                               geojson=feature_collection,
                               activities=all_activities,
                               select_activities=select_activities,
                               month=month,
                               year=year,
                               total=total_str,
                               figure=figure,
                               aggregation_var=aggregation_var,
                               monitoring=monitoring,
                               display=display)
        #return jsonify(feature_collection)


    @app.route('/map_RRM/', methods=['GET', 'POST'])
    def map_rrm(aggregation="baladiya", display="circles", monitoring="all"):
        aggregation = request.form.get("aggregation") if request.form.get("aggregation") else aggregation
        monitoring = request.form.get("monitoring") if request.form.get("monitoring") else monitoring
        display = request.form.get("display") if request.form.get("display") else display
        if aggregation == "mantika":
            aggregation_list1 = ["activity", "mantika"]
        elif aggregation == "baladiya":
            aggregation_list1 = ["activity", "mantika", "baladiya"]
        elif aggregation == "distributionpoint":
            aggregation_list1 = ["activity", "mantika", "baladiya", "distributionpoint"]
        aggregation_var = aggregation_list1[-1]
        aggregation_list2 = []
        for x in aggregation_list1:
            aggregation_list2.append(getattr(distribution_points2, x))
        query_db = query_db = db.session.query(
            distribution_points2.geom.st_union().st_centroid().ST_AsGeoJSON(),  # Taking the centroid per Baladiya
            distribution_points2.activity,
            func.min(distribution_points2.distributionpoint).label("distributionpoint"),
            func.min(distribution_points2.mantika).label("mantika"),
            func.min(distribution_points2.baladiya).label("baladiya"),
            func.bool_or(distributionfigures_rrm.moomken).label("moomken"),
            func.bool_or(distributionfigures_rrm.wfp).label("wfp"),
            func.sum(distributionfigures_rrm.hh_reached).label("hh")).join(  # Joining disrib figures
                distributionfigures_rrm, and_(
                    distribution_points2.id == distributionfigures_rrm.distribution_point,
                    distributionfigures_rrm.hh_reached > 0)).group_by(*aggregation_list2)
        response = query_db.all()
        if request.form.get("download"):
            return excel.make_response_from_query_sets(response, aggregation_list1 + ["moomken", "wfp", "hh"], "xls", file_name="RRM_HH_Reached.xls")
        my_geojson = []
        total_str = "0"
        if [x.hh for x in response]:
            max_hh = max([x.hh for x in response])
            total = sum([x.hh for x in response]) * 5
            total_str = '{:,}'.format(total)
            for x in response:
                if display == "circles":
                    circle_size = sqrt(x.hh / max_hh)
                elif display == "points":
                    circle_size = 0.2
                if monitoring == "all":
                    opacity = 0.7
                elif monitoring == "wfp":
                    opacity = 0.2
                    if x.wfp is True:
                        opacity = 0.7
                elif monitoring == "moomken":
                    opacity = 0.2
                    if x.moomken is True:
                        opacity = 0.7
                feature = Feature(geometry=json.loads(x[0]),
                                  properties={
                                      "mantika": x.mantika,
                                      "baladiya": x.baladiya,
                                      "activity": x.activity,
                                      "moomken": x.moomken,
                                      "wfp": x.wfp,
                                      "distributionpoint": x.distributionpoint,
                                      "circle_size": circle_size,
                                      "circle_color": "#2A93FC",
                                      "circle_opacity": opacity,
                                      'ind': (x.hh) * 5,
                                      'ind_str': '{:,}'.format((x.hh) * 5)})
                my_geojson.append(feature)
        feature_collection = FeatureCollection(my_geojson)
        return render_template("map.html",
                               geojson=feature_collection,
                               total=total_str,
                               aggregation_var=aggregation_var,
                               monitoring=monitoring,
                               display=display)
