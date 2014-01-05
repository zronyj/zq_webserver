activate_this = '/home/ubuntu/chem_server/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/ubuntu/chem_server/")

from chemserver2 import app as application
