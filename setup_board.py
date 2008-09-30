from couch_util import couch_request

# create the pieces
pieces = {}

elements = ['fire','water','plant']
ranks = 3
players = ['red','blue']

for player in players:
  for element in elements:
    for rank in xrange(1,ranks+1):
      tag = "%s-%s%s" % (player,element,rank)
      pieces[tag] = {'kind':element,'rank':rank,'player':player}
  wiztag = "%s-wizard" % player
  pieces[wiztag] = {'kind':'wizard','rank':0,'player':player}


setup_string = """
red-fire2   red-water1  red-wizard  red-plant1  red-water3
red-plant3  red-plant2  red-fire1   red-water2  red-fire3
-           -           -           -           -
-           -           -           -           -
blue-fire3  blue-water2 blue-fire1  blue-plant2 blue-plant3
blue-water3 blue-plant1 blue-wizard blue-water1 blue-fire2
"""

setup = [line.strip().split() for line in setup_string.splitlines() if line.strip()]
for y in xrange(len(setup)):
  for x in xrange(len(setup[y])):
    tag = setup[y][x]
    if tag != '-':
      pieces[tag]['location'] = [x,y]
      
game = {'pieces':pieces, 'turn':'red'}
couch_request('game',201,'PUT',body=game)