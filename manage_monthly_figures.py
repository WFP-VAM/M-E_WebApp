"""
WFP Libya CO DP Manager.

Flask functions to manage the monthly distribution figures:
    - Create and Update (update_GFD)
    - Read (monthly_distrib)
    - Delete (delete_GFD)
    - Export (download_gfd)

To do: Rename GFD with monthly as the functions have been generalised to other activities.
"""

from flask import render_template, redirect, url_for, request
from sqlalchemy import and_
from extensions import db, excel
from models import Wfp_lists, distribution_points2, distributionfigures_gfd


def manage_monthly_figures(app):

    @app.route("/monthly_distrib", methods=["GET", "POST"])
    @app.route("/monthly_distrib/<path:activity>/<int:month>/<int:year>", methods=["GET", "POST"])
    def monthly_distrib(activity='GFD', month=None, year=None):
        """Get the list of monthly distribution points and match it with the ditribution figures for the selected month."""
        if request.form:
            month = request.form.get("newmonth")
            year = request.form.get("newyear")
            activity = request.form.get("newactivity")
        data = db.session.query(distribution_points2, distributionfigures_gfd)
        data = data.filter(distribution_points2.activity == activity)
        data = data.outerjoin(distributionfigures_gfd, and_(
            distribution_points2.id == distributionfigures_gfd.distribution_point,
            distributionfigures_gfd.month == month, distributionfigures_gfd.year == year)).order_by(distribution_points2.id)
        data = data.all()
        activities = Wfp_lists.query.filter_by(type="activity").with_entities(Wfp_lists.name).all()
        return render_template("monthly_distrib.html", data=data, month=month, year=year, activities=activities, selected_activity=activity)

    @app.route("/update_GFD", methods=["POST"])
    def update_GFD():
        """Add or Update a monthly ditribution figure."""
        hh_reached = request.form.get("distri_new_hh_reached")
        hh_planned = request.form.get("distri_new_hh_planned")
        distri_id = request.form.get("distri_id")
        month = request.form.get("month")
        year = request.form.get("year")
        activity = request.form.get("activity")
        moomken = "moomken" in request.form
        wfp = "wfp" in request.form
        distri = distributionfigures_gfd.query.filter_by(distribution_point=distri_id, month=month, year=year).first()
        if distri is None:  # Add a new figure
            newdistri = distributionfigures_gfd(
                distribution_point=distri_id,
                month=month,
                year=year,
                hh_reached=hh_reached,
                hh_planned=hh_planned,
                moomken=moomken,
                wfp=wfp
            )
            db.session.add(newdistri)
        else:  # Update the figure
            distri.moomken = moomken
            distri.wfp = wfp
            distri.hh_reached = hh_reached
            distri.hh_planned = hh_planned

        db.session.commit()
        return redirect(url_for('monthly_distrib', month=month, year=year, activity=activity))

    @app.route("/delete_GFD", methods=["POST"])
    def delete_GFD():
        """Delete a monthly ditribution figure for a selected month."""
        distri_id = request.form.get("distri_id")
        month = request.form.get("month")
        year = request.form.get("year")
        activity = request.form.get("activity")
        distri = distributionfigures_gfd.query.filter_by(distribution_point=distri_id, month=month, year=year).first()
        db.session.delete(distri)
        db.session.commit()
        return redirect(url_for('monthly_distrib', month=month, year=year, activity=activity))

    @app.route("/export_GFD", methods=["GET", "POST"])
    def download_gfd():
        """Export to Excel the list of monthly distribution points and match it with the ditribution figures for the selected month."""
        month = request.form.get("month")
        year = request.form.get("year")
        activity = request.form.get("activity")
        gfd_data = distribution_points2.query.filter_by(activity=activity)
        gfd_data = gfd_data.join(distributionfigures_gfd, distribution_points2.id == distributionfigures_gfd.distribution_point)
        gfd_data = gfd_data.add_columns(distribution_points2.id, distribution_points2.geom, distribution_points2.mantika, distribution_points2.baladiya, distribution_points2.muhalla, distribution_points2.activity,
                                        distributionfigures_gfd.hh_reached, distributionfigures_gfd.hh_planned, distributionfigures_gfd.moomken, distributionfigures_gfd.wfp,
                                        distributionfigures_gfd.month, distributionfigures_gfd.year)
        gfd_data = gfd_data.filter_by(month=month, year=year)
        gfd_data = gfd_data.all()
        # To do: add latitude, longitude to the results (difficult because the gfd_data is a list of immutable tuples)
        return excel.make_response_from_query_sets(gfd_data, ["id", "activity", "month", "year", "mantika", "baladiya", "muhalla", "moomken", "wfp", "hh_reached", "hh_planned"], "xls", file_name=str(activity) + "_" + str(month) + "_" + str(year) + ".xls")
