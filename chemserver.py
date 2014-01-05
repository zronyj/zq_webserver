import flask
import logging
import werkzeug
from flask.ext.restful import reqparse, MethodView
from Firefly import Firefly
from ADVina import ADVina
from AD4 import AD4

chemserver = flask.Flask(__name__)

logging.basicConfig(filename='server.log', format='%(asctime)s - %(message)s', filemode='w', level=logging.INFO)

chemserver.add_url_rule('/firefly/', view_func=Firefly.as_view('firefly'), methods=['GET', 'POST'])
chemserver.add_url_rule('/autodock/', view_func=AD4.as_view('autodock'), methods=['GET', 'POST'])
chemserver.add_url_rule('/advina/', view_func=ADVina.as_view('advina'), methods=['GET', 'POST'])

chemserver.debug = True
if __name__ == '__main__':
	chemserver.run()
