import flask
import os
import shutil
import logging
import smtplib
import threading
import subprocess
import werkzeug
from flask.ext.restful import reqparse, MethodView
from email.Utils import formatdate
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email import Encoders

chemserver = flask.Flask(__name__)

datos = ""
ALLOWED_EXTENSIONS = set(['zip'])
threads = []

logging.basicConfig(filename='server.log', format='%(asctime)s - %(message)s', filemode='w', level=logging.INFO)
f = open("data","r")
user_name = f.readline()[:-1]
pass_word = f.readline()
f.close()

def clean_threads(threads=threads):
    ctrl = 0
    for t in threads:
        if t.isAlive():
            ctrl += 1
    if ctrl == 0:
        return []
    else:
        return threads

def send_mail(para, titulo, contenido, adjuntos=[]):
    msg = MIMEMultipart()
    msg['Subject'] = titulo
    msg['From'] = user_name
    msg['Date'] = formatdate(localtime=True)
    msg['To'] = para
    msg.attach( MIMEText(contenido) )
    # Attaching the file
    if len(adjuntos) != 0:
        for item in adjuntos:
            if item in os.listdir('.'):
                logging.info('Output file found! Processing ...')
                results = open(item,'r').read()
                part = MIMEBase('application', "octet-stream")
                part.set_payload( results )
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(item))
                msg.attach(part)
            else:
                logging.warning('Output file not found.')
                results = "The input file had errors and no output coulf be generated."
    try:
        logging.info('Trying to establish connection through SMTP.')
        s = smtplib.SMTP('smtp.gmail.com',587)
        s.ehlo()
        s.starttls()
        s.ehlo
        s.login(user_name, pass_word)
        s.sendmail(user_name, [para], msg.as_string())
        s.quit()
        logging.info('email sent to: ' + para)
    except Exception as e:
        logging.error('Connection failed! email was not sent.')
        logging.error(e)

class Firefly(MethodView):

    def __init__(self):
        logging.info('Firefly class started! Waiting for user to make requests.')
    
    def get(self):
        return flask.render_template('firefly.html')

    def post(self):
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
        subprocess.call(['../Firefly/FF7.1G/firefly', '-f',
                         '-i', os.getcwd() + '/temp.inp',
                         '-o', os.getcwd() + '/temp.out'])
        send_mail(self.correo, 'Results of Firefly calculation', "Your output file is ready and was attached to this email.", ["temp.inp","temp.out"])
        send_mail('zronyj@yahoo.com', 'Results of Firefly calculation', "Your output file is ready and was attached to this email.", ["temp.inp","temp.out"])
        os.remove('temp.inp')
        os.remove('temp.out')
        os.chdir('..')

class AD4(MethodView):

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[-1] in ALLOWED_EXTENSIONS

    def __init__(self):
        self.working_dir = os.getcwd() + '/ad4_files/'
        logging.info('AutoDock4 class started! Waiting for user to make requests.')
    
    def get(self):
        return flask.render_template('ad4.html')

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
            threads.append(threading.Thread(target=self._run_docking))
            threads[-1].start()
            return flask.render_template('alt1.html')

    def _run_docking(self):
        logging.info('Change directory and unzip files.')
        os.chdir('./ad4_files')
        subprocess.call(['unzip',os.path.join(os.getcwd() + '/', self.nombre)])
        logging.info('Running autogrid and autodock.')
        subprocess.call(['../AD4/autogrid4','-p','grid.gpf','-l','grid.glg'])
        subprocess.call(['../AD4/autodock4','-p','dock.dpf','-l','dock.dlg'])
        all_files = os.listdir(os.getcwd())
        if self.nombre in all_files:
            all_files.remove(self.nombre)
        logging.info('Compressing all files.')
        subprocess.call(['zip','temp_out.zip'] + all_files)
        send_mail(self.correo, 'Results of AutoDock4 calculation', "Your output files are ready and were attached to this email as a zip file.", [self.nombre,"temp_out.zip"])
        send_mail('zronyj@yahoo.com', 'Results of AutoDock4 calculation', "Your output files are ready and were attached to this email as a zip file.", [self.nombre,"temp_out.zip"])
        logging.info('Changing directory, deleting files and recreating the folder.')
        os.chdir('..')
        shutil.rmtree(os.getcwd() + '/ad4_files')
        os.mkdir('ad4_files')

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

    def _run_docking_vina(self):
        logging.info('Change directory and unzip files.')
        os.chdir('./advina_files')
        subprocess.call(['unzip',os.path.join(os.getcwd() + '/', self.nombre)])
        logging.info('Running AutoDock Vina.')
        subprocess.call(['../ADVina/vina','--config',os.getcwd() + '/conf.txt'])
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


chemserver.add_url_rule('/firefly/', view_func=Firefly.as_view('firefly'), methods=['GET', 'POST'])
chemserver.add_url_rule('/autodock/', view_func=AD4.as_view('autodock'), methods=['GET', 'POST'])
chemserver.add_url_rule('/advina/', view_func=ADVina.as_view('advina'), methods=['GET', 'POST'])

chemserver.debug = True
if __name__ == '__main__':
	chemserver.run()
