"""
WFP Libya CO DP Manager.

Extension file to avoid circular imports from db
"""

from flask_sqlalchemy import SQLAlchemy
import flask_excel as excel

db = SQLAlchemy()
