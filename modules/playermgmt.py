"""This backend module handles all player and group related actions"""

from gluon import current
from gluon import html
from gluon import http
import datetime
import pdb

def ensure_session_vars(auth, inreguser=False):
    '''Ensures that the current.session contains expected info'''
    db = current.db

    if current.session.saved_userid != auth.user.id:
        current.session.playerid = None
        current.session.saved_userid = None
        current.session.playgroup = None
        current.session.all_playgroups = None
        current.session.groupplayers = None
        current.session.guestplayer = None
        current.session.data_valid = False
        current.session.playerdata_updated = None

    if not current.session.playerid:
        #get the player associated with the authenticated user
        playerid = None
        for row in db(db.auth_user.id == auth.user.id
                     ).select(db.auth_user.player):
            playerid = row.player
            break
        current.session.playerid = playerid
        current.session.saved_userid = auth.user.id
        current.session.data_valid = False
        if playerid != None:
            current.session.playerdata_updated = db.player[playerid].last_update


    if current.session.playerid != None:
        if (current.session.playerdata_updated == None or
            current.session.playerdata_updated < db.player[playerid].last_updated):
            current.session.data_valid = False

    if current.session.playgroup:
        #If we're in a playgroup, check that the data isn't stale

        db_updated = db.playgroup[current.session.playgroup["id"]].last_update
        try:
            if (current.session.playgroup["last_update"] == None or
                    current.session.playgroup["last_update"] < db_updated):
                current.session.data_valid = False
        except KeyError:
            current.session.data_valid = False



    if (not current.session.playgroup or
        current.session.data_valid == False):
        #get the playgroup info associated with the player
        playgroup = None
        all_playgroups = []

        for row in db(
                (db.groupplayer.player == current.session.playerid) &
                ((db.groupplayer.role == "admin") |
                 (db.groupplayer.role == "member"))
                     ).select(db.playgroup.id,
                              db.playgroup.name,
                              db.playgroup.last_update,
                              db.playgroup.useronly,
                              db.groupplayer.defaultgroup,
                              join=db.playgroup.on(
                                  db.groupplayer.playgroup == db.playgroup.id)
                             ):
            playgroup = {"name": row.playgroup.name,
                         "id": row.playgroup.id,
                         "useronly": row.playgroup.useronly,
                         "last_update": row.playgroup.last_update}
            all_playgroups.append(playgroup)
        
            if row.groupplayer.defaultgroup == True:
                current.session.playgroup = playgroup

        current.session.all_playgroups = all_playgroups

        if current.session.playgroup:
            current.session.groupplayers = get_playgroup_players(
                current.session.playgroup["id"])
            guest = db(
                (db.groupplayer.playgroup == current.session.playgroup["id"]) &
                (db.player.guestplayer == True)
                ).select(db.player.name, db.player.id)[0]

            current.session.guestplayer = {"name": guest.name, "id": guest.id}

    current.session.data_valid = True

    # If the user has not registered yet, forward user to user creation page
    if current.session.playerid == None and not inreguser:
        http.redirect(html.URL('register', 'register'))


def set_active_playgroup(group):
    '''Sets the active playgroup for a player'''
    db = current.db
    for pg in current.session.all_playgroups:
        if group == pg["id"]:
            current.session.playgroup = pg
            current.session.groupplayers = get_playgroup_players(group)
            guest = db(
                (db.groupplayer.playgroup == group) &
                (db.player.guestplayer == True)
                ).select(db.player.name, db.player.id)[0]

            current.session.guestplayer = {"name": guest.name, "id": guest.id}

            db((db.groupplayer.defaultgroup == True) & 
               (db.groupplayer.player == current.session.playerid)).update(
                    defaultgroup=False)

            db((db.groupplayer.playgroup == group) & 
               (db.groupplayer.player == current.session.playerid)).update(
                    defaultgroup=True)
            break


def is_playername_free(name):
    '''Checks if playername is free'''

    db = current.db
    if db(db.player.name.like(name)).select().first() != None:
        return False
    else:
        return True

def get_playername(player):
    '''Returns the player name for the id'''

    db = current.db
    player = db(db.player.id == player).select(
        cache=(current.cache.ram, 300)).first()
    if player != None:
        return player.name
    else:
        return ""

def get_playernames():
    '''Return all playernames'''
    db = current.db
    players = db().select(db.player.name,
                          cache=(current.cache.ram, 300)).as_list()
    return [player["name"] for player in players]


def get_invitable_players(playgroup):
    '''Return playername and id for players that can be invited'''
    db = current.db

    if playgroup in [p["id"] for p in current.session.all_playgroups]:
        pgplayers = [p["id"] for p in get_playgroup_players(playgroup)]
        players = db(db.player.guestplayer == False).select(
                     db.player.name, db.player.id).as_list()
        retplayers = []
        #Filter out entries of players in multiple playgroups
        for player in players:
            if player["id"] not in pgplayers:
                retplayers.append(player)

        return retplayers
    else:
        raise ValueError

def register_player(auth, name):
    '''Creates a player for this username'''

    db = current.db
    if not is_playername_free(name):
        raise ValueError
    else:
        playerid = db.player.insert(name=name,
                                    guestplayer=False,
                                    linked=True)
        db.auth_user[auth.user.id] = dict(player=playerid)
        current.session.playerid = playerid

        #Create a personal group to start with
        create_group("Just me", useronly=True, defgroup=True)


def add_player(playgroup, name):
    '''Adds a player to the playgroup'''

    db = current.db
    if is_groupadmin(playgroup):
        if not is_playername_free(name):
            raise ValueError
        else:
            playerid = db.player.insert(name=name,
                                        guestplayer=False,
                                        linked=False,
                                        last_update=datetime.datetime.now())
            db.groupplayer.insert(player=playerid,
                                  playgroup=playgroup,
                                  role="member")
            db.playgroup[playgroup] = dict(
                last_update=datetime.datetime.now())
    else:
        raise ValueError

def merge_players(playgroup, sourceid, targetid):
    '''Merges an unlinked player with a linked player.
    This also means changing ids in
     - old games
     - ongoing games
     - decks
    '''

    db = current.db
    if is_groupadmin(playgroup):
        try:
            if is_player_playing(sourceid):
                raise PlayerException("Player has an active game")

            sourceplayer = db(
                (db.groupplayer.player == sourceid) &
                (db.groupplayer.playgroup == playgroup)
                ).select(db.groupplayer.id,
                         db.groupplayer.player,
                         db.player.linked,
                         join=db.player.on(
                             db.groupplayer.player == db.player.id)
                        ).first()


            targetplayer = db(
                (db.groupplayer.player == targetid) &
                (db.groupplayer.playgroup == playgroup)
                ).select(db.groupplayer.id,
                         db.groupplayer.player,
                         db.player.linked,
                         join=db.player.on(
                             db.groupplayer.player == db.player.id)
                        ).first()

        except IndexError:
            raise ValueError
        if (sourceplayer.player.linked == False and
                targetplayer.player.linked == True):
            sourceid = sourceplayer.groupplayer.player
            targetid = targetplayer.groupplayer.player
            db(db.deck.owner == sourceid).update(owner=targetid)
            db(db.game_players.player == sourceid).update(player=targetid)
            db(db.ongoing_game_players.player == sourceid).update(
               player=targetid)
            db(db.groupplayer.player == sourceid).delete()
            db(db.player.id == sourceid).delete()
            db.playgroup[playgroup] = dict(last_update=datetime.datetime.now())
        else:
            raise ValueError

    else:
        raise ValueError



def set_admin(playgroup, playerid, admin):
    '''Sets/removes admin privileges
    Admins can't edit themselves'''

    db = current.db
    if is_groupadmin(playgroup):
        if playerid != current.session.playerid:
            try:
                admplayer = db(
                    (db.groupplayer.player == playerid) &
                    (db.groupplayer.playgroup == playgroup)
                    ).select(db.groupplayer.id).first()
                if admin:
                    db.groupplayer[admplayer.id] = dict(role="admin")
                else:
                    db.groupplayer[admplayer.id] = dict(role="member")
                db.playgroup[playgroup] = dict(last_update=datetime.datetime.now())

            except IndexError:
                raise ValueError
        else:
            raise ValueError
    else:
        raise ValueError


def is_groupadmin(playgroup):
    '''Is the current player the admin for his/her group?'''

    db = current.db
    link = db((db.groupplayer.player == current.session.playerid) &
              (db.groupplayer.role == "admin") &
              (db.groupplayer.playgroup == playgroup)
             ).select().first()
    if link != None:
        return True
    else:
        return False

def is_player_playing(playerid):
    db = current.db
    games = db(db.ongoing_game_players.player == playerid).select()
    if len(games) != 0:
        return True
    else:
        return False

def get_group_invited(playgroup):
    '''Get the invited players for the group'''

    db = current.db
    players = db(
        (db.groupplayer.playgroup == playgroup) &
        (db.groupplayer.role == "invited")
        ).select(db.player.name,
                 db.player.id,
                 join=db.player.on(
                     db.groupplayer.player == db.player.id)
                ).as_list()
    return players

def is_groupname_free(name):
    '''Checks if groupname is free.'''

    db = current.db
    if db(db.playgroup.name.like(name)).select().first() != None:
        return False
    else:
        return True

def get_playgroup_players(playgroup):
    '''Returns all players in a playgroup'''

    db = current.db
    players = db(
        (db.groupplayer.playgroup == playgroup) &
        (db.player.id == db.groupplayer.player) &
        (db.player.guestplayer == False)
        ).select(db.player.id,
                 db.player.name,
                 db.player.linked,
                 db.groupplayer.role)
    return [{"id": row.player.id,
             "name": row.player.name,
             "linked": row.player.linked,
             "role": row.groupplayer.role} for row in players]

def create_group(name, useronly=False, defgroup=False):
    '''Creates a playgroup with this name'''

    db = current.db
    role = "member"
    if not useronly:
        role = "admin"
        # All personal groups have the same name
        if not is_groupname_free(name):
            raise ValueError

    groupid = db.playgroup.insert(name=name,
                                  last_update=datetime.datetime.now(),
                                  open=False,
                                  useronly=useronly)
    guestid = db.player.insert(name="Guest",
                               guestplayer=True,
                               linked=True)
    db.groupplayer.insert(player=current.session.playerid,
                          playgroup=groupid,
                          role=role,
                          defaultgroup=defgroup)
    db.groupplayer.insert(player=guestid,
                          playgroup=groupid,
                          role="member")
    db.player[current.session.playerid] = dict(
        last_update=datetime.datetime.now())


    current.session.data_valid = False

def invite_player(playgroup, playername):
    '''Invite a player to the current group'''

    db = current.db
    if is_groupadmin(playgroup):
        player = db(db.player.name == playername).select(db.player.id).first()
        if player != None:
            db.groupplayer.insert(player=player["id"],
                                  playgroup=playgroup,
                                  role="invited")
        else:
            raise ValueError
    else:
        raise ValueError


def cancel_invitation(playgroup, playerid):
    '''Cancel an invitiation'''

    db = current.db
    if is_groupadmin(playgroup):7151753e1d41
        player = db(db.player.id == playerid).select(db.player.id).first()
        if player != None:
            db((db.groupplayer.player == player.id) &
               (db.groupplayer.playgroup == playgroup) &
               (db.groupplayer.role == "invited")).delete()
        else:
            raise ValueError
    else:
        raise ValueError


def join_group(playgroup):
    '''Join group if invited'''

    db = current.db
    groupplayer = db(
        (db.groupplayer.player == current.session.playerid) &
        (db.groupplayer.role == "invited") &
        (db.groupplayer.playgroup == playgroup)
        ).select(db.groupplayer.playgroup, db.groupplayer.id).first()
    if groupplayer != None:
        db.groupplayer[groupplayer.id] = dict(role="member")
        db.playgroup[playgroup] = dict(last_update=datetime.datetime.now())

    db.player[current.session.playerid] = dict(
        last_update=datetime.datetime.now())

    current.session.data_valid = False



def get_invited_groups(player=None):
    '''Gets the invited groups for either current player,
    or player from argument'''

    db = current.db
    playerid = None
    if player == None:
        playerid = current.session.playerid
    else:
        playerid = player

    playgroups = db(
        (db.groupplayer.player == playerid) &
        (db.groupplayer.role == "invited")
        ).select(db.playgroup.name,
                 db.playgroup.id,
                 join=db.playgroup.on(
                     db.groupplayer.playgroup == db.playgroup.id)
                ).as_list()

    return playgroups


class PlayerException(Exception):
    "Exception for invalid player states."
    def __init__(self, message=None):
        Exception.__init__(self)
        self.message = message
