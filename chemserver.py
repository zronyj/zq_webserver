import flask
import logging
import werkzeug
from flask.ext.restful import reqparse, MethodView
from Firefly import Firefly
from ADVina import ADVina
from AD4 import AD4
from Welcome import Welcome

app = flask.Flask(__name__)

schlussel = open('key','r')
app.secret_key = schlussel.readline()
schlussel.close()

logging.basicConfig(filename='server.log', format='%(asctime)s - %(message)s', filemode='w', level=logging.INFO)

app.add_url_rule('/firefly/', view_func=Firefly.as_view('firefly'), methods=['GET', 'POST'])
app.add_url_rule('/autodock/', view_func=AD4.as_view('autodock'), methods=['GET', 'POST'])
app.add_url_rule('/advina/', view_func=ADVina.as_view('advina'), methods=['GET', 'POST'])
app.add_url_rule('/welcome/', view_func=Welcome.as_view('welcome'), methods=['GET', 'POST'])

app.debug = True
if __name__ == '__main__':
	app.run()
