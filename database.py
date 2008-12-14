from settings import db_server, db_name
import couchdb

server = couchdb.Server(db_server)

if db_name not in server:
  server.create(db_name)
db = server[db_name]

"""
def view_sync():
  from dbviews import views
  from couchdb.design import ViewDefinition as View
  View.sync_many(db,views,remove_missing=True)
"""
