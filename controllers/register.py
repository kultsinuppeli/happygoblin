import playermgmt
import game
import gluon.contrib.simplejson
from gluon import html
from gluon import http

@auth.requires_login()
def register():
  response.loginmenu = [
        (T('Login/Register'),
            URL('default', 'user') == URL(),
            URL('default', 'user'),
            []),
    ]
  playermgmt.ensure_session_vars(auth, inreguser=True)
  # If the user has already registered, forward user to user the index page
  if current.session.playerid != None:
      http.redirect(html.URL('default', 'index'))
  return dict()

 
@auth.requires_login()
def check_username():
  playermgmt.ensure_session_vars(auth, inreguser=True)
  response.generic_patterns = ['json']
  
  try:    
    return {"free": playermgmt.is_playername_free(request.vars.name)}
  except:
    return {"free": False}

@auth.requires_login()
def create_user():
  playermgmt.ensure_session_vars(auth, inreguser=True)
  response.generic_patterns = ['json']
  
  try: 
    playername = gluon.contrib.simplejson.loads(request.body.read())["playername"]

    if playername != None and playername != "":
      playermgmt.register_player(auth, playername)
      return {}
    else:
      raise HTTP(403)
  except:
    raise HTTP(403)
    
  
@auth.requires_login()
def check_groupname():
  playermgmt.ensure_session_vars(auth)
  response.generic_patterns = ['json']
  
  try:    
    return {"free":  playermgmt.is_groupname_free(request.vars.name)}
  except:
    return {"free": False}

  