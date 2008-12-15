map_chats = """
function(doc){
if(doc.type == "chat"){
  emit([doc.game, doc.timestamp], {"type":"chat", "user":doc.user, "name":doc.name, "timestamp":doc.timestamp, 
                                  "text":doc.text})  
  }
}"""

map_events = """
function(doc){
  if(doc.type == "chat"){
    emit([doc.game, doc.timestamp], {"type":"chat", "user":doc.user, "name":doc.name, "timestamp":doc.timestamp, 
                                    "text":doc.text})  
  } else if(doc.type == "move"){
    emit([doc.game, doc.timestamp], {"type":"move", "user":doc.user, "name":doc.name, "timestamp":doc.timestamp, 
                                    "from_space":doc.from_space, "to_space":doc.to_space })
  }
}"""

map_games = """
function(doc){
  if(doc.type == "game"){
    emit(null,{"players":doc.players})
  }
}
"""

map_users = """
function(doc){
  if(doc.type == "user"){
    emit(doc.slug, {"name":doc.name})
  }
}"""

from couchdb.design import ViewDefinition as View
users  = View('users','show',map_users)
games  = View('games','show',map_games)
events = View('events','all',map_events)
chats = View('events','chats',map_chats)

views = [users,games,events,chats]

def view_sync():
  from database import db
  View.sync_many(db,views,remove_missing=True)
