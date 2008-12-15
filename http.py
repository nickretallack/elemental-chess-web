import web

def badrequest(message):
  return web.HTTPError("400 Bad Request", {}, message)
  
def forbidden(message):
  return web.HTTPError("403 Forbidden", {}, message)

def unacceptable(message):
  return web.HTTPError("406 Not Acceptable", {}, message)

def precondition(message):
  return web.HTTPError("412 Precondition Failed", {}, message)
