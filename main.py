#!/usr/bin/env python
from views import *
from urls import urls

import web
if __name__ == "__main__":
  web.webapi.internalerror = web.debugerror   # enables debugger
  web.run(urls, globals(), web.reloader)

