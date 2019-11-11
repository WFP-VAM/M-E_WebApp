"""
WFP Libya CO DP Manager.

Flask functions to manage the list of activities and partners (same table):
    - Create and Update (update_wfp_list)
    - Read (wfp_list)
    - Delete (delete_wfp_list)
"""

from flask import render_template, redirect, url_for, request
from extensions import db
from models import Wfp_lists


def manage_partners_activities(app):

    @app.route("/wfp_list/<path:type>", methods=["GET", "POST"])
    def wfp_list(type=None):
        """Access the list of partners or activities."""
        data = Wfp_lists.query.filter_by(type=type).all()
        return render_template("partners_and_activities.html", data=data, type=type)

    @app.route("/update_wfp_list", methods=["GET", "POST"])
    def update_wfp_list():
        """Update the list of partners or activities."""
        id = request.form.get("id")
        type = request.form.get("type")
        if id is None:
            new_id = Wfp_lists(name=request.form.get("name"), type=type)
            db.session.add(new_id)
        else:
            id_query = Wfp_lists.query.filter_by(id=id).first()
            id_query.name = request.form.get("name")
        db.session.commit()
        return redirect(url_for('wfp_list', type=type))

    @app.route("/delete_wfp_list", methods=["GET", "POST"])
    def delete_wfp_list():
        """Delete one partner or activity."""
        if request.form:
            id = request.form.get("id")
            type = request.form.get("type")
            id_query = Wfp_lists.query.filter_by(id=id).first()
            db.session.delete(id_query)
            db.session.commit()
        return redirect(url_for('wfp_list', type=type))
