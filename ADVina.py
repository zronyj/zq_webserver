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

ALLOWED_EXTENSIONS = set(['zip'])

class ADVina(MethodView):

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[-1] in ALLOWED_EXTENSIONS

    def __init__(self):
        self.working_dir = os.getcwd() + '/advina_files/'
        logging.info('AutoDock Vina class started! Waiting for user to make requests.')
    
    def get(self):
        return flask.render_template('advina.html')

    def post(self):
        threads = clean_threads()
        logging.info('User requested to add new data.')
        self.archivo = flask.request.files['file']
        self.correo = flask.request.form.get('mail')
        print type(self.archivo.filename)
        if self.archivo and self.allowed_file(self.archivo.filename):
            self.nombre = werkzeug.secure_filename(self.archivo.filename)
            self.archivo.save(os.path.join(self.working_dir, self.nombre))
            logging.info('Data loaded.')
            threads.append(threading.Thread(target=self._run_docking_vina))
            threads[-1].start()
            return flask.render_template('alt1.html')
        return flask.render_template('alt2.html')

    def _run_docking_vina(self):
        logging.info('Change directory and unzip files.')
        os.chdir('./advina_files')
        subprocess.call(['unzip',os.path.join(os.getcwd() + '/', self.nombre)])
        logging.info('Running AutoDock Vina.')
        subprocess.call(['../../ADVina/vina','--config',os.getcwd() + '/conf.txt'])
        all_files = os.listdir(os.getcwd())
        if self.nombre in all_files:
            all_files.remove(self.nombre)
        logging.info('Compressing all files.')
        subprocess.call(['zip','temp_out.zip'] + all_files)
        send_mail(self.correo, 'Results of AutoDock Vina calculation', "Your output files are ready and were attached to this email as a zip file.", [self.nombre,"temp_out.zip"])
        send_mail('zronyj@yahoo.com', 'Results of AutoDock Vina calculation', "Your output files are ready and were attached to this email as a zip file.", [self.nombre,"temp_out.zip"])
        logging.info('Changing directory, deleting files and recreating the folder.')
        os.chdir('..')
        shutil.rmtree(os.getcwd() + '/advina_files')
        os.mkdir('advina_files')
