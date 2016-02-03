import game
import playermgmt
import pdb

# -*- coding: utf-8 -*-
### required - do no delete
def user():
    response.loginmenu = [
        (T('Login/Register'),
            URL('default', 'user') == URL(),
            URL('default', 'user'),
            []),
    ]
    return dict(form=auth())

def download(): return response.download(request, db)
def call(): return service()
### end requires

@auth.requires_login()
def index():
    playermgmt.ensure_session_vars(auth)

    return dict()

@auth.requires_login()
def active_playgroup():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']

    try:
        playermgmt.set_active_playgroup(int(request.vars.group))
    except:
        pass

    return dict()

def error():
    return dict()

@auth.requires_login()
def list_games():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']

    amount = None

    try:
        amount = int(request.vars.amount)
    except:
        pass
    return {"games": game.list_games(amount)}

@auth.requires_login()
def list_ongoing_games():
    playermgmt.ensure_session_vars(auth)
    response.generic_patterns = ['json']

    return {"games": game.list_ongoing_games()}

def about():
    response.loginmenu = [
        (T('Login/Register'),
            URL('default', 'user') == URL(),
            URL('default', 'user'),
            []),
    ]

    return {}

def contact():
    response.loginmenu = [
        (T('Login/Register'),
            URL('default', 'user') == URL(),
            URL('default', 'user'),
            []),
    ]

    return {}
