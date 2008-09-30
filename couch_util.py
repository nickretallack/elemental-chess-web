from settings import database_url
import simplejson as json
from httplib2 import Http
http = Http()

def couch_request(path,expected,*args,**kwargs):
  url = "%s/%s" % (database_url,path)
  if 'body' in kwargs:
    kwargs['body'] = json.dumps(kwargs['body'])
  response,content = http.request(url, *args, **kwargs )
  if response.status != expected:
    print "Unexpected Status %d:%s for %s "%(response.status,response.reason,url)
  return json.loads(content)