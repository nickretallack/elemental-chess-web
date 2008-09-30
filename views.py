from couch_util import couch_request

from web.cheetah import render

def setup(pieces):
  width = 5
  height = 6
  spaces = [[None for x in xrange(width)] for y in xrange(height)]
  for piece in pieces:
    x,y = pieces[piece]['location']
    spaces[y][x] = piece
  return spaces

class index:
  def GET(self):
    game = couch_request('game',200)
    #print game['pieces']
    board = setup(game['pieces'])
    #print pieces
    render('simple.html',{'board':board})

class move:
  def POST(self):
    print "moving"
