from settings import database_url

import simplejson as json
from httplib2 import Http
http = Http()

#create the database
try:
  response, content = http.request(database_url, 'PUT')
  print response.reason
except:
  print "Connection Refused.  Is couchdb running?"