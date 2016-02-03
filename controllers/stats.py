import game
import playermgmt
import deckmgmt
import gluon.contrib.simplejson


@auth.requires_login()
def stats():
    playermgmt.ensure_session_vars(auth)
    return {"decks": deckmgmt.list_decks(player_only=False)}

@auth.requires_login()
def filter():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']
    
    try:
        filters = gluon.contrib.simplejson.loads(request.body.read())
        games = game.get_games_for_stats(filters)
        stats = game.get_stats(games)
        stats["games"] = games
        return stats
    except:
        raise HTTP(403)
    