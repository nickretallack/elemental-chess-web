#!/usr/bin/env python

if __name__ == "__main__":
  import web
  web.config.debug = True
  
  from views import application
  application.run()
