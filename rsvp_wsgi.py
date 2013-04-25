#!/usr/bin/env python2.7

import os
import sys
import logging

from ournewballandchain import create_app, ProductionConfig
application = create_app(ProductionConfig)


from flask import current_app, request

@application.before_first_request
def setup_logging():
    
    current_app.logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    current_app.logger.addHandler(sh)

@application.before_request
def log_requests():
    application.logger.info("%s - %s", request.method, request.url) 