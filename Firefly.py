import flask
import os
import logging
import smtplib
import threading
import subprocess
import werkzeug
from flask.ext.restful import reqparse, MethodView
from mail_handler import *

class Firefly(MethodView):

    def __init__(self):
        logging.info('Firefly class started! Waiting for user to make requests.')

    @login_required
    def get(self):
        return flask.render_template('firefly.html')

    @login_required
    def post(self):
	global threads
	threads = clean_threads()
        logging.info('User requested to add new data.')
        parser = reqparse.RequestParser()
        parser.add_argument('data',type=str)
        parser.add_argument('mail',type=str, help='Invalid email address.')
        args = parser.parse_args()
        self.datos = args['data']
        self.correo = args['mail']
        cf = open('firefly_files/temp.inp','w')
        cf.write(self.datos)
        cf.close()
        logging.info('Data added.')
        threads.append(threading.Thread(target=self._run_calculation))
        threads[-1].start()
        return flask.render_template('alt1.html')

    def _run_calculation(self):
        logging.info('Changing directory ...')
        os.chdir('./firefly_files')
        logging.info('Attempting to run Firefly.')
        subprocess.call(['../../Firefly/FF7.1G/firefly', '-f',
                         '-i', os.getcwd() + '/temp.inp',
                         '-o', os.getcwd() + '/temp.out'])
        send_mail(self.correo, 'Results of Firefly calculation', "Your output file is ready and was attached to this email.", ["temp.inp","temp.out"])
        send_mail('zronyj@yahoo.com', 'Results of Firefly calculation', "Your output file is ready and was attached to this email.", ["temp.inp","temp.out"])
        os.remove('temp.inp')
        os.remove('temp.out')
        os.chdir('..')
