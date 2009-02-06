from database import db
import web # for exceptions.  Yeah I'm being lazy.  I know this couples badly
import dbview

class User:
  SlugCache = {}
  IDCache = {}
  
  @classmethod
  def all(cls):
    instances = []
    for record in dbview.users(db).rows:
      instance = User(record)
      cls.IDCache[instance.id] = cls.SlugCache[instance.slug] = instance
      instances.append(instance)
    return instances  
  
  @classmethod
  def get(cls, slug=None, id=None):
    if id:
      if not id in db:
        raise web.notfound()
      record = db[id]
      if record['type'] != "user":
        raise web.notfound()
    if slug:
      records = dbview.users(db, startkey=slug, endkey=slug).rows
      if not len(records):
        raise web.notfound()
      record = records[0]

    instance = User(record)
    cls.SlugCache[instance.slug] = cls.IDCache[instance.id] = instance
    return instance

  def __init__(self, params):
    #print params
    if 'value' in params:
      self.name = params['value']['name']
      self.slug = params['key']
      self.id = params['id']
    else:
      self.name = params['name']
      self.slug = params['slug']
      self.id   = params['_id']


class Game:
  IDCache = {}

  def __init__(self, params):
    if 'value' in params:
      self.player_ids = params["value"]["players"]
      #self.order = params["value"]["order"]
      #self.timestamp = params[""]
      self.id = params["id"]
    else:
      self.player_ids = params['players']
      self.order = params['order']
      self.turn  = params['turn']
      self.timestamp = params['timestamp']
      self.board = params['board']
      self.id = params['_id']
      
    self._players = None

  def get_players(self):
    if not self._players:
      #print self.player_ids
      self._players = dict([(color, User.get(id=id)) for (color,id) in self.player_ids.items()])
    return self._players

  players = property(get_players)
      
  @classmethod
  def get(cls, id=None):
    if id:
      if not id in db:
        raise web.notfound()
      record = db[id]
      if record['type'] != "game":
        raise web.notfound()
      
    instance = Game(record)
    cls.IDCache[instance.id] = instance
    return instance

  @classmethod
  def all(cls):
    instances = []
    for record in dbview.games(db).rows:
      instance = Game(record)
      cls.IDCache[instance.id] = instance
      instances.append(instance)
    return instances
  


if __name__ == "__main__":
  #print User.get(slug="kalufurret").name
  #print Game.all()[0].players
  #print User.all()
  game = Game.get(id="e4725af328f248c6b32cc52d3cb932c1")
  for (color,player) in game.players.items():
    print player.id

# import web
# from database import db
# import dbview
# 
# class Indirect
#   class __impl:
#     pass
# 
#   __cached = {}
#   def __init__(self, args):
#     id = args.id
#     if id in __cached:
#       self.__instance = __cached[id]
#     else:
#       self.__instance = __cached[id] = __impl(args)
#       self.__record   = db[id]
# 
#   def __getattr__(self, attr):
#     return getattr(self.__instance, attr)
#   
#   def __setattr__(self, attr, value):
#     return setattr(self.__instance, attr, value)
# 
# class User(Indirect):
#   class __impl:
#     def __init__(self, args):
#       pass
#     
#     def name(self):
#       self.__record["name"]
# 
# class Game:
#   class __impl:    
#     def __init__(self, args):
#       self.id = args.id
#       if "value" in args:
#         # it was queried from a view
#         self.player_ids = args["value"]["players"]
#       else:
#         # we have the whole game object
#         self.player_ids = args["players"]
#         self.board = args["board"]
#         self.turn  = args["turn"]
#         self.order = args["order"]
#   
#     def players():
#       
#       #[{"name": db[player_id].name, "color":color} for (color, player_id) in self.player_ids]  
#   
#     @classmethod
#     def all(cls):
#       return memo ||= [Game(game) for game in dbview.games(db)]  
#   
#     @classmethod
#     def get(cls, game_id):
#       if game_id not in db:
#         raise web.notfound()
# 
#       game = db[game_id]
#       if game['type'] != "game":
#         raise web.notfound()
# 
#       return Game(game)
