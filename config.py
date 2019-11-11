"""
WFP Libya CO DP Manager.

Config file.
"""

import os

class Config(object):
    BASIC_AUTH_USERNAME = os.environ['BASIC_AUTH_USERNAME']
    BASIC_AUTH_PASSWORD = os.environ['BASIC_AUTH_PASSWORD']
    BASIC_AUTH_FORCE = True
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
