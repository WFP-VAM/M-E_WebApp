"""
WFP Libya CO DP Manager.

Flask functions to manage the list of distribution points:
    - Create and Update (update_distrib_point)
    - Read (home)
    - Delete (delete_distrib_point)
    - Export to Excel (download_file)
"""

import datetime

from flask import render_template, redirect, url_for, request

from geoalchemy2 import func
from geoalchemy2.shape import to_shape
from geoalchemy2.comparator import Comparator

from extensions import db, excel

from models import libya_admin2, libya_admin3, libya_admin4, distribution_points2, Wfp_lists

today = datetime.date.today()
last_month = today - datetime.timedelta(days=30)


def manage_distribution_points(app):

    @app.route("/admin", methods=["GET", "POST"])
    def home(lon=13.180161, lat=32.885353):
        """Admin home page to manage the distribution points."""
        all_data_db = distribution_points2.query.all()
        add_lat_lon(all_data_db)
        partners = Wfp_lists.query.filter_by(type="partner").all()
        activities = Wfp_lists.query.filter_by(type="activity").all()
        return render_template("home.html", all_data_db=all_data_db, data=(lon, lat), month=last_month.month, year=last_month.year, partners=partners, activities=activities)

    @app.route("/update_distrib_point", methods=["GET", "POST"])
    def update_distrib_point():
        """
        Update or create a new distribution point.
        For a given set of coordinates, it finds the Mantika (polygon)
        countaining the point and the closest Baladiya (point) and Muhalla (point)
        within the Mantika
        """
        id = request.form.get("id")
        distributionpoint = request.form.get("name_detailed")
        lon = request.form.get("longitude")
        lat = request.form.get("latitude")
        point = 'SRID=4326;POINT(' + lon + ' ' + lat + ')'
        mantika_q = db.session.query(libya_admin2.adm2_manti, libya_admin2.geom).filter(func.ST_Contains(libya_admin2.geom, point)).first()
        if mantika_q is None:
            wrong_coords = "Error: Coordinates " + lon + ", " + lat + " are not in Libya"
            return redirect(url_for('error', message=wrong_coords))
        mantika = mantika_q.adm2_manti
        baladiya = db.session.query(libya_admin3.adm3_balad) \
            .filter(func.ST_within(libya_admin3.geom, mantika_q.geom)) \
            .order_by(Comparator.distance_centroid(libya_admin3.geom, point)).limit(1).first()[0],  # Filters Baladiya (Points) in Mantika (Polygon) and finds the closest one to submited Point (KNN search with tree index)
        muhalla = db.session.query(libya_admin4.adm4_muhal) \
                    .filter(func.ST_within(libya_admin4.geom, mantika_q.geom)) \
                    .order_by(Comparator.distance_centroid(libya_admin4.geom, point)).limit(1).first()[0]  # Filters Muhalla (Points) in Mantika (Polygon) and finds the closest one to submited Point (KNN search with tree index)
        distri_point = distribution_points2.query.filter_by(id=id).first()
        if distri_point is None:
            new_distri_point = distribution_points2(
                distributionpoint=distributionpoint,
                partner=request.form.get("selectcp"),
                activity=request.form.get("selectactivity"),
                idps=request.form.get("idps") in ["True"],
                returnees=request.form.get("returnees") in ["True"],
                nondisplaced=request.form.get("nondisplaced") in ["True"],
                migrants=request.form.get("migrants") in ["True"],
                comments=request.form.get("comments"),
                geom=point,
                mantika=mantika,
                baladiya=baladiya,
                muhalla=muhalla
            )
            db.session.add(new_distri_point)
        else:
            distri_point.distributionpoint = distributionpoint
            distri_point.geom = point
            distri_point.mantika = mantika
            distri_point.baladiya = baladiya
            distri_point.muhalla = muhalla
        db.session.commit()
        return redirect(url_for('home'))

    @app.route("/delete_distrib_point", methods=["POST"])
    def delete_distrib_point():
        """Delete a Distribution Point."""
        id = request.form.get("id")
        distrib = distribution_points2.query.filter_by(id=id).first()
        db.session.delete(distrib)
        db.session.commit()
        return redirect(url_for('home'))

    @app.route("/export", methods=["GET", "POST"])
    def download_file():
        """Export to Excel list of Distribution Points."""
        all_data_db = distribution_points2.query.all()
        add_lat_lon(all_data_db)
        return excel.make_response_from_query_sets(all_data_db, ["id", "latitude", "longitude", "distributionpoint", "mantika", "baladiya", "muhalla", "activity", "idps", "returnees", "nondisplaced", "migrants", "comments"], "xls", file_name="WFP_distribution_points.xls")

    @app.route("/error", methods=["GET", "POST"])
    def error():
        """Error route with a specific message."""
        my_message = request.args.get('message')
        return render_template("error.html", error_message=my_message)

    def add_lat_lon(my_list):
        """Get the longitude and latitude from a list of PostGIS geometry objects."""
        i = 0
        for x in my_list:
            my_list[i].latitude = to_shape(x.geom).y
            my_list[i].longitude = to_shape(x.geom).x
            i += 1
        return my_list
