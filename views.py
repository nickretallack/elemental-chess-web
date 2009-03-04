import web
from database import db
import dbview
#from couch_util import couch_request

COUCH_MAX = u"\u9999"

from helper import render, get_you, get_game, require_you, make_timestamp
from dbview import *
import http

try:
  import json
except ImportError:
  import simplejson as json


from game_model import User, Game

class IndexView:
  def GET(self):
    you = get_you()
    games = Game.all()
    users = User.all()
    return render("index", games=games, users=users, you=get_you())

class UserView:
  def GET(self, slug):
    user = User.get(slug=slug)
    return render("user", user=user, you=get_you())
    

class GameView:
  def GET(self, game_id):
    game = Game.get(game_id)
    chats = dbview.chats(db, endkey=[game_id, ''], startkey=[game_id, COUCH_MAX], descending=True)
    you = get_you()
    
    #players = dict([(color, db[player_id]) for (color,player_id) in game["players"].iteritems()])

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if you:
      your_players = [color for (color,player) in game.players.items() if player.id == you.id]
      #print "Your Players: %s" % game.players.items()[0].id
    else:
      print "NOTHING"
      your_players = []
      
    return render('game',game=game, you=get_you(), chats=chats, your_players=your_players)


class GameEventsView:
  def GET(self, game_id, timestamp):

    events = dbview.events(db, startkey=[game_id, timestamp], endkey=[game_id, COUCH_MAX]).rows

    if not len(events): # no events have happened in this game yet, most likely
      return json.dumps({"timestamp":timestamp})
    
    newest_timestamp = events[-1].key[1] # highly dependent on query
    new_events = [event.value for event in events if event.key[1] != timestamp]
    if not len(new_events):
      return "{}"
      
    return json.dumps({"timestamp":newest_timestamp, "events":new_events})


class GamesView:
  def POST(self):
    you = require_you()
    params = web.input()

    if not params["user"]:
      return web.notfound()
    
    user = dbview.users(db, startkey=params['user'], endkey=params['user']).rows
    if not len(user):
      return web.notfound()
    else:
      user = user[0]
    
    from setup_board import board
    game = {"type":"game", "board":board, "timestamp":make_timestamp(), "turn":0, 
            "players":{"red":you.id,"blue":user.id}, "order":["red","blue"]}
    game_id = db.create(game)
    web.seeother("/games/%s" % game_id)


class GameChatView:
  #def GET(self, game_id):  # could just give us the chats, for debug purposes
  
  def POST(self, game_id):
    you = require_you()
    game = get_game(game_id)

    params = web.input(text='')
    text = params["text"]
    if len(text) == 0:
      raise http.unacceptable("Chat messages must contain some text")

    chat = {"type":"chat", "text":text, "game":game_id, "user":you.id, "name":you["name"]}
    
    # synchronize timestamps
    game["timestamp"] = chat["timestamp"] = make_timestamp()    
    db[game_id] = game
    db.create(chat)
    return "OK"


class GameMoveView:
  def POST(self, game_id):
    you = require_you()
    game = get_game(game_id)

    params = web.input(from_space=None, to_space=None)
    if not (params["from_space"] and params["to_space"]):
      raise http.badrequest("Moves must include from_space and to_space")

    from_space = tag_2d(params["from_space"])
    to_space   = tag_2d(params["to_space"])
    
    if not (len(from_space) == len(to_space) == 2):
      raise http.badrequest("Invalid space tags")

    # check if it's your turn
    player = game["order"][game["turn"] % len(game["order"])]
    if game["players"][player] != you.id:
      raise http.precondition("It's not your turn")

    board = game["board"]
    attacking_piece = game["board"][from_space[0]][from_space[1]]

    if attacking_piece == None:
      raise http.forbidden("No piece to move from %s" % params["from_space"])

    if attacking_piece["player"] != player:
      raise http.forbidden("It's not %s's turn" % attacking_piece["player"])

    if not valid_move(attacking_piece["kind"], from_space, to_space):
      raise http.forbidden("You can't move %s from %s to %s" % (attacking_piece["kind"], params["from_space"], params["to_space"]))
    
    defending_piece = game["board"][to_space[0]][to_space[1]]
    if defending_piece != None:
    
      if attacking_piece["player"] == defending_piece["player"]:
        raise http.forbidden("You can't attack yourself")
    
      if not battle(attacking_piece["kind"], defending_piece["kind"]):
        raise http.forbidden("You can't beat %s with %s" % (defending_piece["kind"], attacking_piece["kind"]))
      
    # actually move the piece
    game["board"][from_space[0]][from_space[1]] = None
    game["board"][to_space[0]][to_space[1]] = attacking_piece
    
    # advance the turn
    game["turn"] += 1

    # trigger an event
    move = {"type":"move", "game":game_id, "user":you.id, "name":you["name"],
            "from_space":params["from_space"], "to_space":params["to_space"]}
    
    # update timestamps just before saving
    game["timestamp"] = move["timestamp"] = timestamp = make_timestamp()    
    db[game_id] = game
    move_id = db.create(move)
      
    return timestamp



class SettingsView:
  def GET(self):
    return render("settings", you=require_you())
  
  def POST(self):
    you = require_you()
    params = web.input(name='')

    unique = True
    name = params['name']
    if name and name != you.get('name',None):
      from helper import slugify
      slug = slugify(name)
      for row in dbview.users(db, startkey=slug, endkey=slug):
        if slug == row.key:
          unique = False
          break
    
      if unique:
        you['name'] = name
        you['slug'] = slug
    elif not name and 'name' in you:
      # blanking your name makes you anonymous, and makes your page inaccessible
      del you['name']
      del you['slug']

    db[you.id] = you

    if unique:
      web.redirect('/')
    else:
      return render('settings', errors="Sorry, that name's taken!", you=you)


urls = (
    '/',      IndexView,
    '/login', web.openid.host,
    '/settings', SettingsView,
    '/users/(.*)', UserView,
    #'/chat',  Chat,
    '/games/(.*)/events/(.*)', GameEventsView,
    '/games/(.*)/moves',  GameMoveView,
    '/games/(.*)/chat',  GameChatView,
    '/games/(.*)', GameView,
    '/games',  GamesView,
    )

application = web.application(urls, locals())





type_advantages = {"fire":"plant", "plant":"water", "water":"fire"}

def tag_2d(tag):
  return [int(x) for x in tag.split('-')]

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
  elif (kind == "wizard") and (abs(from_space[0] - to_space[0]) == 1) and (abs(from_space[1] - to_space[1]) == 1):
    return True   # moved one space on each axis
