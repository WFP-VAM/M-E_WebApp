"""
WFP Libya CO DP Manager.

Flask functions to manage the RRM cumulative distribution figures:
    - Create and Update (update_RRM)
    - Read (distrib_rrm)
    - Delete (delete_RRM)
    - Export (export_rrm)
"""

from flask import render_template, redirect, url_for, request
from extensions import db, excel
from models import distribution_points2, distributionfigures_rrm


def manage_cumulative_figures(app):
    @app.route("/distrib_RRM", methods=["GET", "POST"])
    def distrib_rrm():
        """Get the list of RRM distribution points and match it with the ditribution figures."""
        data = distribution_points2.query.filter_by(activity='RRM')
        data = data.outerjoin(distributionfigures_rrm, distribution_points2.id == distributionfigures_rrm.distribution_point)
        data = data.add_columns(distribution_points2.id, distribution_points2.distributionpoint,
                                distribution_points2.mantika, distribution_points2.baladiya, distribution_points2.muhalla,
                                distribution_points2.activity, distribution_points2.partner, distributionfigures_rrm.hh_reached,
                                distributionfigures_rrm.moomken, distributionfigures_rrm.wfp).order_by(distribution_points2.id)
        data = data.all()
        return render_template("distrib_rrm.html", data=data)

    @app.route("/update_RRM", methods=["POST"])
    def update_RRM():
        """Add or Update a RRM ditribution figure."""
        distri_new_hh_reached = request.form.get("distri_new_hh_reached")
        distri_id = request.form.get("distri_id")
        moomken = "moomken" in request.form
        wfp = "wfp" in request.form
        distri = distributionfigures_rrm.query.filter_by(distribution_point=distri_id).first()
        if distri is None:
            newdistri = distributionfigures_rrm(
                distribution_point=distri_id,
                hh_reached=distri_new_hh_reached,
                moomken=moomken,
                wfp=wfp
            )
            db.session.add(newdistri)
        else:
            distri.moomken = moomken
            distri.wfp = wfp
            distri.hh_reached = distri_new_hh_reached
        db.session.commit()
        return redirect(url_for('distrib_rrm'))

    @app.route("/delete_RRM", methods=["POST"])
    def delete_RRM():
        """Delete a RRM ditribution figure."""
        distri_id = request.form.get("distri_id")
        distri = distributionfigures_rrm.query.filter_by(distribution_point=distri_id).first()
        db.session.delete(distri)
        db.session.commit()
        return redirect(url_for('distrib_rrm'))

    @app.route("/export_rrm", methods=["GET", "POST"])
    def download_rrm():
        """Export to Excel the list of RRM distribution points and match it with the ditribution figures."""
        data = distribution_points2.query.filter_by(activity='RRM')
        data = data.join(distributionfigures_rrm, distribution_points2.id == distributionfigures_rrm.distribution_point)
        data = data.add_columns(distribution_points2.id, distribution_points2.mantika, distribution_points2.baladiya, distribution_points2.muhalla, distribution_points2.activity,
                                distributionfigures_rrm.hh_reached, distributionfigures_rrm.moomken, distributionfigures_rrm.wfp)
        data = data.all()
        return excel.make_response_from_query_sets(data, ["id", "activity", "mantika", "baladiya", "muhalla", "moomken", "wfp", "hh_reached"], "xls", file_name="RRM_HH_Reached.xls")
