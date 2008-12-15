import web
from database import db
import jinja2
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'), line_statement_prefix="#")


def user_name(user):
  if 'name' in user:
    return user['name']
  else:
    return "anonymous"

def hex_color(seed,invert=False):
  import random
  random.seed(seed)
  color = random.randint(0,16**6)
  if invert:
    color = 16**6 - color
  return "%X" % color

env.filters['len'] = len
env.filters['user_name'] = user_name
env.filters['hex_color'] = hex_color
import json
env.filters['json'] = json.dumps


def render(template,**args):
  return env.get_template(template+'.html').render(**args)

def get_you():
  openid = web.openid.status()
  if openid:
    key = "user-%s" % openid
    if key in db:
      return db[key]
    else:
      you = {'type':'user', 'openids':[openid], "name":"no-name"}
      db[key] = you
      return you

def get_game(game_id):
  if game_id not in db:
    raise web.notfound()

  game = db[game_id]
  if game['type'] != "game":
    raise web.notfound()

  return game

def require_you():
  you = get_you()
  if not you:
    raise web.HTTPError("401 unauthorized", {}, "You must be logged in")
  return you

  
def make_timestamp():
  from datetime import datetime
  return datetime.now().isoformat()  
  
  
# Modified slugging routines originally stolen from patches to django
def slugify(value):
  """ Normalizes string, converts to lowercase, removes non-alpha characters,
  and converts spaces to hyphens.  """
  import unicodedata
  import re
  #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
  value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
  return re.sub('[-\s]+', '-', value)
