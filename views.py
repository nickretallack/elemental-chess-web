import web
from database import db
#from couch_util import couch_request

import jinja2
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'), line_statement_prefix="#")
env.filters['len'] = len

def render(template,**args):
  return env.get_template(template+'.html').render(**args)

"""
class Piece(object):
  def __init__(self,options):
    self.rank = options['rank']
    self.kind = options['kind']
    self.player = options['player']
    self.x, self.y = options['location']

  def tag(self):
    return "%s-%s%d" % (self.player, self.kind, self.rank)

  def __str__(self):
    return tag()

class Target(object):
  def __init__(self,piece,x,y):
    self.piece = piece
    self.x = x
    self.y = y

  def __str__(self):
    return "%s|%s|%s" % (piece.tag(),x,y)

class Game(object):
  def __init__(self):
    # retrieve game state
    game = couch_request('game',200)
    #self.pieces = game['pieces']
    self.width = 5
    self.height = 6

    # build some local indexes
    self.spaces = [[{} for x in xrange(self.width)] for y in xrange(self.height)]
    for piece_opts in game['pieces']:
      piece = Piece(piece_opts)
      self.spaces[piece.y][piece.x]['piece'] = piece
      self.pieces[piece.tag()] = piece

  def mark_moves(self,piece_tag):
    piece = self.pieces[piece_tag]
    x,y = piece.x, piece.y
    for move in [(x+1,y),(x,y+1),(x-1,y),(x,y-1)]:
      nx,ny = move
      if nx >= 0 and nx < self.width and ny >= 0 and ny < self.height: # make sure move lands on the board
        target = self.spaces[ny][nx]
        # unsafe wording....
        if not 'piece' in target or self.battle(piece_tag,target['piece']): # see if move is legal
          self.spaces[ny][nx]['target'] = Target(piece)
    
  def battle(self,attacker_tag,defender_tag):
    attacker = self.pieces[attacker_tag]
    defender = self.pieces[defender_tag]
    if int(attacker['rank']) < int(defender['rank']):
      True
    
      

def mark_valid_moves(piece,board):
  x,y = piece['location']
  for move in [(x+1,y),(x,y+1),(x-1,y),(x,y-1)]:
    nx,ny = move
    if nx >= 0 and nx < len(board[y]) and ny >= 0 and ny < len(board): # make sure move lands on the board
      target = board[ny][nx]
      # unsafe wording....
      if not 'piece' in target or battle(piece,target['piece']): # see if move is legal
        board[ny][nx]['target'] = piece
"""   
  
def get_you():
  openid = web.openid.status()
  if openid:
    key = "user-%s" % openid
    if key in db:
      return db[key]
    else:
      you = {'type':'user', 'openids':[openid]}
      db[key] = you
      return you

  
  
def make_timestamp():
  from datetime import datetime
  return datetime.now().isoformat()  
  
find_chats = """
function(doc){
  if(doc.type == "chat"){
    emit(doc.timestamp, {"text":doc.text})
  }
}"""

find_games = """
function(doc){
  if(doc.type == "game"){
    emit(doc._id,1)
  }
}
"""
  
  

class Index:
  def GET(self):
    games = db.query(find_games).rows
    chats = db.query(find_chats).rows
    return render("index", chats=chats, games=games, timestamp=chats[-1].key, you=get_you())

class Chat:
  def POST(self):
    # this is an event
    params = web.input(text='')
    event = {"type":"chat", "timestamp":make_timestamp(), "text":params["text"]}
    db.create(event)
    return ''
  
  def GET(self):
    import json
    params = web.input(timestamp=make_timestamp())
    chats = db.query(find_chats, startkey=params["timestamp"]).rows
    if(len(chats)):
      timestamp = chats[-1].key
    else:
      timestamp = params["timestamp"]
      
    new_chats = [chat.value for chat in chats if chat.key != params["timestamp"]]  
    return json.dumps({"timestamp":timestamp, "chats":new_chats})
    #return json.dumps(chats)
    #game = Game()
    #render('simple.html',{'board':game.spaces})


class Event:
  def GET(self):
    events = db.query(find_chats)


def tag_2d(tag):
  return [int(x) for x in tag.split('-')]
  

class Move:
  def POST(self, game_id):
    you = get_you()
    if not you: # TODO
      raise web.notfound() # how about access denied instead?
    
    if game_id not in db:
      raise web.notfound

    params = web.input(from_space=None, to_space=None)
    if not (params["from_space"] and params["to_space"]):
      web.ctx.status = 400
      return "Moves must include from_space and to_space"

    from_space = tag_2d(params["from_space"])
    to_space   = tag_2d(params["to_space"])
    
    if not (len(from_space) == len(to_space) == 2):
      web.ctx.status = 400
      return "Invalid space tags"
            
    game   = db[game_id]
    board = game["board"]
    attacking_piece = game["board"][from_space[0]][from_space[1]]

    if attacking_piece == None:
      return "No piece to move from %s" % params["from_space"]

    if attacking_piece["player"] != "red": # TODO
      return "You don't have a piece on %s" % params["from_space"]

    if not valid_move(attacking_piece["kind"], from_space, to_space):
      #web.ctx.status = 401
      return "You can't move %s from %s to %s" % (attacking_piece["kind"], params["from_space"], params["to_space"])
    
    defending_piece = game["board"][to_space[0]][to_space[1]]
    if defending_piece != None:
    
      if attacking_piece["player"] == defending_piece["player"]:
        #web.ctx.status = 401
        return "You can't attack yourself"
    
    
      if not battle(attacking_piece["kind"], defending_piece["kind"]):
        #web.ctx.status = 401
        return "You can't beat %s with %s" % (defending_piece["kind"], attacking_piece["kind"])
      
    # actually move the piece
    game["board"][from_space[0]][from_space[1]] = None
    game["board"][to_space[0]][to_space[1]] = attacking_piece
    
    # TODO: advance the turn?
    
    db[game_id] = game
    
    # trigger an event
    move = {"type":"move", "user":you.id, "timestamp":make_timestamp(),
            "from_space":params["from_space"], "to_space":params["to_space"]}
    
    db.create(move)
      
    return "OK"


type_advantages = {"fire":"plant", "plant":"water", "water":"fire"}



def battle(attacker, defender):
  if attacker == "wizard": return False
  if defender == "wizard": return True
  attacker_type = attacker[:-1]
  defender_type = defender[:-1]
  if type_advantages[attacker_type] == defender_type: return True
  if type_advantages[defender_type] == attacker_type: return False
  attacker_level = int(attacker[-1])
  defender_level = int(defender[-1])
  if attacker_level > defender_level: return True
  return False


def valid_move(kind, from_space, to_space):
  if abs(from_space[0] - to_space[0]) + abs(from_space[1] - to_space[1]) == 1:
    return True   # only moved one space

  # if to_space[0] == from_space[0]:
  #   if abs(to_space[1] - from_space[1]) == 1:
  #     return True
  # elif to_space[1] == from_space[1]
  #   if abs(to_space[0] - from_space[0]) == 1:
  #     return True
  
  elif (kind == "wizard") and (abs(from_space[0] - to_space[0]) == 1) and (abs(from_space[1] - to_space[1]) == 1):
    return True   # moved one space on each axis



"""
    params = web.input(piece=None,target=None)
    if params.piece:
      # user selected a piece
      game = Game()
      game.mark_moves(params.piece)
      render('simple.html',{'board':game.spaces})
      
    elif params.target:
      pass
      # user tried to move the piece
"""      

class Game:
  def GET(self, game_id):
    if game_id not in db:
      raise web.notfound()
      
    game = db[game_id]
    if game['type'] != "game":
      raise web.notfound()

    return render('game',game=game)
  



class Games:
  def POST(self):
    you  = get_you() or "TEST"
    if not you: return "You must be logged in to create a game"
    from setup_board import board
    game = {"type":"game", "players":{"red":you}, "board":board, "turn":"red"}
    game_id = db.create(game)
    web.seeother("/game/%s" % game_id)



urls = (
    '/',      Index,
    '/login', web.openid.host,
    '/games/(.*)/move',  Move,
    '/chat',  Chat,
    '/games',  Games,
    '/games/(.*)', Game,
    )

application = web.application(urls, locals())