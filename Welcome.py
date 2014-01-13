import flask
import os
import shutil
import logging
import smtplib
import threading
import subprocess
import werkzeug
from flask.ext.restful import reqparse, MethodView
from mail_handler import *

stuff = {'user':'password'}

class Welcome(MethodView):

    def get(self):
        return flask.render_template('welcome.html')

    def post(self):
        if 'logout' in flask.request.form:
            logging.info('User requested to log out.')
            flask.session.pop('username', None)
            return flask.redirect(flask.url_for('welcome'))
        logging.info('User requested to log in.')
        required = ['usuario', 'clave']
        for i in required:
            if i not in flask.request.form:
                flask.flash("Error: {0} is a required field.".format(i))
                logging.info('User did not send complete login data.')
                return flask.redirect(flask.url_for('welcome'))
        logging.info('User sent everything.')
        parser = reqparse.RequestParser()
        parser.add_argument('usuario',type=str)
        parser.add_argument('clave',type=str)
        args = parser.parse_args()
        self.user = args['usuario']
        self.passw = args['clave']
        if self.user in stuff and stuff[self.user] == self.passw:
            logging.info('User ' + self.user + ' is in!')
            flask.session['username'] = self.user
        else:
            logging.info('User tried with incorrect info: username - ' + self.user + ' password - ' + self.passw)
            flask.flash(flask.Markup("The username or password you entered is <b>incorrect</b>."))
        return flask.redirect(flask.url_for('welcome'))
            
        
        return flask.render_template('welcome.html')
