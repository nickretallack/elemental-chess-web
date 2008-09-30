from couch_util import couch_request

from web.cheetah import render
import web

class Piece(object):
  def __init__(self,options):
    self.rank = options['rank']
    self.kind = options['kind']
    

class Target(object):
  pass


class Game(object):
  def __init__(self):
    # retrieve game state
    game = couch_request('game',200)
    self.pieces = game['pieces']
    self.width = 5
    self.height = 6

    # set up board view
    self.spaces = [[{} for x in xrange(self.width)] for y in xrange(self.height)]
    for piece_opts in game['pieces']:
      piece = Piece(piece_opts)
      x,y = game['pieces'][piece]['location']
      self.spaces[y][x] = {'piece':piece}

  def mark_moves(self,piece_tag):
    piece = self.pieces[piece_tag]
    x,y = piece['location']
    for move in [(x+1,y),(x,y+1),(x-1,y),(x,y-1)]:
      nx,ny = move
      if nx >= 0 and nx < self.width and ny >= 0 and ny < self.height: # make sure move lands on the board
        target = self.spaces[ny][nx]
        # unsafe wording....
        if not 'piece' in target or self.battle(piece_tag,target['piece']): # see if move is legal
          self.spaces[ny][nx]['target'] = piece
    
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
      
  

class index:
  def GET(self):
    game = Game()
    render('simple.html',{'board':game.spaces})

class move:
  def POST(self):
    params = web.input(piece=None,target=None)
    if params.piece:
      # user selected a piece
      game = Game()
      game.mark_moves(params.piece)
      render('simple.html',{'board':game.spaces})
      
    elif params.target:
      pass
      # user tried to move the piece