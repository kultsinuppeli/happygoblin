import playermgmt
import game
import deckmgmt
import config
import gluon.contrib.simplejson
from gluon.contrib.websocket_messaging import websocket_send

@auth.requires_login()
def ingame():
    playermgmt.ensure_session_vars(auth)
    try:
        return {"game_id": request.vars.game_id,
                "websocket_server": config.websocket_server}
    except AttributeError:
        pass
    return dict()

@auth.requires_login()
def get_deck_names():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']

    return {'decks': [deck["name"] for deck in 
                      deckmgmt.list_decks(player_only=False)]}

@auth.requires_login()
def get_game_state():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']

    return game.get_ongoing_game(request.vars.game_id)

@auth.requires_login()
def discard_game():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']
    game.discard_game(request.vars.game_id)
    return dict()

@auth.requires_login()
def end_game():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']
    wininfo = gluon.contrib.simplejson.loads(request.body.read())

    try:
        saveid = game.end_game(request.vars.game_id, wininfo)
        websocket_send("http://" + config.websocket_server, 
                       gluon.contrib.simplejson.dumps(
                            {"gameFinished": True}),
                            config.websocket_key,
                            str(request.vars.game_id))
        return {"saveid": saveid}  
    #except game.storeGameException as e:
    except e:
        pass


@auth.requires_login()
def update_game_info():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']
    
    update_fields = gluon.contrib.simplejson.loads(request.body.read())
    changed = game.update_game(request.vars.game_id, update_fields)
    websocket_send("http://" + config.websocket_server,
                   gluon.contrib.simplejson.dumps(changed),
                   config.websocket_key,
                   str(request.vars.game_id))


    return dict()

