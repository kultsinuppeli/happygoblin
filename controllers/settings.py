import playermgmt
import deckmgmt
import game
import gluon.contrib.simplejson


@auth.requires_login()
def decks():
    '''Display settings'''
    response.submenu = [
        (T('Playgroup'),
            URL('settings', 'playgroup') == URL(),
            URL('settings', 'playgroup'),
            []),
        (T('Decks'),
            URL('settings', 'decks') == URL(),
            URL('settings', 'decks'),
            []),
    ]

    playermgmt.ensure_session_vars(auth)

    return {"decks": deckmgmt.list_decks()}

@auth.requires_login()
def playgroup():
    '''Display settings'''
    response.submenu = [
        (T('Playgroup'),
            URL('settings', 'playgroup') == URL(),
            URL('settings', 'playgroup'),
            []),
        (T('Decks'),
            URL('settings', 'decks') == URL(),
            URL('settings', 'decks'),
            []),
    ]

    playermgmt.ensure_session_vars(auth)
    playgroups = session.all_playgroups
    
    for playgroup in playgroups:
        pgplayers = playermgmt.get_playgroup_players(playgroup["id"])
        playgroup["linked_players"] = [player for player in
                            pgplayers if
                            player["linked"]]
        playgroup["unlinked_players"] = [player for player in
                            pgplayers if not
                            player["linked"]]
        playgroup["admin"] = playermgmt.is_groupadmin(playgroup["id"])
        playgroup["invited"] = playermgmt.get_group_invited(playgroup["id"])    
    
    return {"playgroups": playgroups,
            "invites": playermgmt.get_invited_groups()}


@auth.requires_login()
def get_playernames():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']

    return {"players": playermgmt.get_playernames()}

@auth.requires_login()
def get_invitable_players():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']


    try:
        players = playermgmt.get_invitable_players(int(request.vars.playgroup))

        return {"players": [p["name"] for p in players]}
                
    except:
        raise HTTP(403)
    return {"players": playermgmt.get_playernames()}

@auth.requires_login()
def set_admin():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']


    try:
        adminvars = gluon.contrib.simplejson.loads(request.body.read())

        if (adminvars["playerid"] != None and
                adminvars["admin"] != None and
                adminvars["playgroup"] != None):
            playermgmt.set_admin(int(adminvars["playgroup"]),
                                 int(adminvars["playerid"]),
                                 adminvars["admin"])
            return {}
        else:
            raise HTTP(403)
    except:
        raise HTTP(403)


@auth.requires_login()
def add_player():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']


    try:
        playervars = gluon.contrib.simplejson.loads(request.body.read())

        if (playervars["playername"] != None and
                playervars["playgroup"] != None):
            playermgmt.add_player(int(playervars["playgroup"]), 
                                  playervars["playername"])
            return {}
        else:
            raise HTTP(403)
    except:
        raise HTTP(403)

@auth.requires_login()
def merge_players():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']


    try:
        playervars = gluon.contrib.simplejson.loads(request.body.read())
        pdb.set_trace()

        if (playervars["sourceid"] != None and
                playervars["targetid"] != None and
                playervars["playgroup"] != None):
            playermgmt.merge_players(int(playervars["playgroup"]),
                                     int(playervars["sourceid"]),
                                     int(playervars["targetid"]))
            return {}
        else:
            raise HTTP(403)
    except:
        raise HTTP(403)

@auth.requires_login()
def invite_player():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']

    try:
        playervars = gluon.contrib.simplejson.loads(request.body.read())

        if (playervars["playername"] != None and
                playervars["playername"] != "" and
                playervars["playgroup"] != None):
            playermgmt.invite_player(int(playervars["playgroup"]),
                                     playervars["playername"])
            return {}
        else:
            raise HTTP(403)
    except:
        raise HTTP(403)

@auth.requires_login()
def cancel_invitation():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']

    try:
        playervars = gluon.contrib.simplejson.loads(request.body.read())

        if (playervars["playerid"] != None and
                playervars["playgroup"] != None):
            playermgmt.cancel_invitation(int(playervars["playgroup"]),
                                         int(playervars["playerid"]))
            return {}
        else:
            raise HTTP(403)
    except:
        raise HTTP(403)

@auth.requires_login()
def merge_decks():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']

    try:
        deckvars = gluon.contrib.simplejson.loads(request.body.read())

        if deckvars["sourceid"] != None and deckvars["targetid"] != None:
            deckmgmt.merge_decks(int(deckvars["sourceid"]),
                                 int(deckvars["targetid"]))
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

@auth.requires_login()
def is_player_playing():
  playermgmt.ensure_session_vars(auth)
  response.generic_patterns = ['json']
  
  try:
    params = gluon.contrib.simplejson.loads(request.body.read())
    return {"playing": playermgmt.is_player_playing(int(params["player"])), 
            "player": int(params["player"]),
            "playgroup": int(params["playgroup"])}
  except:
    return {}


@auth.requires_login()
def create_group():
  playermgmt.ensure_session_vars(auth)
  response.generic_patterns = ['json']

  try:
    groupname = gluon.contrib.simplejson.loads(request.body.read())["groupname"]

    if groupname != None and groupname != "":
      playermgmt.create_group(groupname)
      return {}
    else:
      raise HTTP(403)
  except:
    raise HTTP(403)
    
@auth.requires_login()
def join_group():
  playermgmt.ensure_session_vars(auth)
  response.generic_patterns = ['json']

  try:
    playgroup = gluon.contrib.simplejson.loads(request.body.read())["playgroup"]
    playermgmt.join_group(int(playgroup))
    return {}
  except:
    raise HTTP(403)
