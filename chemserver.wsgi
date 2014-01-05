#!/usr/bin/python

activate_this = '/var/www/zq_webserver/myvenv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
print "Virtual Environment ready!"

import os
import sys
os.chdir('/var/www/zq_webserver')
sys.path.insert(0,'/var/www/zq_webserver')
print "Path prepared ..." + os.getcwd()

from chemserver import app as application
