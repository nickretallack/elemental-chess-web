#!/usr/bin/env python

if __name__ == "__main__":
  import web
  web.config.debug = True

  from dbview import view_sync
  view_sync()
  
  from views import application
  application.run()
