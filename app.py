"""
WFP Libya CO DP Manager.

Flask Web Application that:
    - manages the Distribution Points (CRUD app)
        - list of activities and partners
        - distrtibution points with spatial informaiton (GPS and administrative boundaries)
    - manages the Distribution Figures linked with the distribution points (CRUD app)
        - Cumulative for RRM
        - Monthly Figure for all activities (GFD, Livelihood, etc.)
    - maps the data (serving geojson to a Mapbox GL JS web map)
"""
from flask import Flask
from flask_basicauth import BasicAuth
from extensions import db, excel
from manage_distribution_points import manage_distribution_points
from manage_monthly_figures import manage_monthly_figures
from manage_cumulative_figures import manage_cumulative_figures
from manage_partners_activities import manage_partners_activities
from map_figures import map_figures

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
excel.init_excel(app)
BasicAuth(app)
manage_distribution_points(app)
manage_partners_activities(app)
manage_monthly_figures(app)
manage_cumulative_figures(app)
map_figures(app)


if __name__ == "__main__":
    app.run(debug=False)
