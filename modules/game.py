"""This backend module handles all game related actions"""
from gluon import current
#from gluon.debug import dbg
import datetime
import deckmgmt
import playermgmt
import pdb

PLAYERAMOUNTS = {
    "Basic": [2, 3, 4, 5, 6],
    "2-headed": [4, 6],
    "Star": [5],
    "Emperor": [6],
    "Archenemy": [3, 4, 5, 6]
}

GAMETYPES = ["Basic", "2-headed", "Star", "Emperor", "Archenemy"]
FORMATS = ["Casual", "Standard", "Block", "Modern", "Legacy",
           "Vintage", "Commander", "Draft", "Sealed"]

def create_game(newgame=None, copyfrom=None):
    '''Creates a new running game based on the given data
    or the previous game id.'''

    db = current.db
    playeramount = 0
    gameformat = ""
    gametype = ""
    game = 1
    decks = ["", "", "", "", "", ""]
    tags = []
    players = []

    p1life = 20
    otherlife = 20
    cmdr_dmg = []
    gameid = None

    if copyfrom != None:
        row = db((db.game.id == copyfrom) &
                 (db.game.playgroup == current.session.playgroup["id"])
                ).select(db.game.ALL).first()
        if row != None:
            oldgame = row
            playeramount = oldgame["playeramount"]
            gameformat = oldgame["format"]
            game = oldgame["game"] + 1
            if game > 3:
                game = 1

            tags = oldgame["tags"]
            gametype = oldgame["gametype"]


            newplayers = db(
                db.game_players.game == copyfrom
                ).select(db.game_players.player,
                         db.game_players.position,
                         db.game_players.deck)
            for player in newplayers:
                if "deck" in player and player.deck != None:
                    decks[player.position-1] = db.deck(player.deck).name
                players.append(player["player"])
        else:
            raise NewGameException("Old game not found")

    elif newgame != None:
        playeramount = int(newgame["playeramount"])
        gameformat = newgame["format"]
        gametype = newgame["gametype"]
        game = 1
        tags = newgame["tags"]
        decks = ["", "", "", "", "", ""]

        players = newgame["players"]

    else:
        raise NewGameException("No new game defined")

    if gameformat == "Commander":
        p1life = 40
        otherlife = 40
        for p in range(len(players)):
            cmdr_dmg.append(0)


    if gametype == "Archenemy":
        p1life *= 2
    elif gametype == "2-headed":
        p1life *= 1.5
        otherlife *= 1.5

    gameid = db.ongoing_game.insert(playgroup=current.session.playgroup["id"],
                                    gametype=gametype,
                                    format=gameformat,
                                    game=game,
                                    onplay=1,
                                    playeramount=playeramount,
                                    timestarted=datetime.datetime.now(),
                                    tags=tags,
                                    p1life=p1life,
                                    p2life=otherlife,
                                    p3life=otherlife,
                                    p4life=otherlife,
                                    p5life=otherlife,
                                    p6life=otherlife,
                                    p1poison=0,
                                    p2poison=0,
                                    p3poison=0,
                                    p4poison=0,
                                    p5poison=0,
                                    p6poison=0,
                                    p1cmdr=cmdr_dmg,
                                    p2cmdr=cmdr_dmg,
                                    p3cmdr=cmdr_dmg,
                                    p4cmdr=cmdr_dmg,
                                    p5cmdr=cmdr_dmg,
                                    p6cmdr=cmdr_dmg,
                                    p1deck=decks[0],
                                    p2deck=decks[1],
                                    p3deck=decks[2],
                                    p4deck=decks[3],
                                    p5deck=decks[4],
                                    p6deck=decks[5]).id

    for pos, player in enumerate(players):
        db.ongoing_game_players.insert(ongoing_game=gameid,
                                       player=player["id"],
                                       position=pos)
    return gameid

def list_ongoing_games():
    '''Lists ongoing games for the playgroup in date order'''

    db = current.db
    games = db(
        db.ongoing_game.playgroup == current.session.playgroup["id"]
        ).select(db.ongoing_game.gametype,
                 db.ongoing_game.format,
                 db.ongoing_game.timestarted,
                 db.ongoing_game.playeramount,
                 db.ongoing_game.id,
                 db.ongoing_game.tags,
                 orderby=~db.ongoing_game.timestarted).as_list()

    for pos, game in enumerate(games):
        #select players, join to get name. build a dict for each player this way
        players = [{
            "id": player["player"]["id"],
            "name": player["player"]["name"]
            } for player in db(
                db.ongoing_game_players.ongoing_game == game["id"]
                ).select(
                    join=db.player.on(
                        db.ongoing_game_players.player == db.player.id)
                    ).as_list()]
        games[pos]["players"] = players

    return games

def list_games(amount=None):
    '''Lists finished games for the playgroup in date order'''

    if amount != None and amount > 0:
        limitby = (0, amount)
    else:
        limitby = None
    db = current.db
    games = db(
        db.game.playgroup == current.session.playgroup["id"]
        ).select(db.game.gametype,
                 db.game.format,
                 db.game.timeended,
                 db.game.playeramount,
                 db.game.id,
                 db.game.tags,
                 orderby=~db.game.timeended,
                 limitby=limitby).as_list()

    for pos, game in enumerate(games):
        #select players, join to get name. build a dict for each player this way
        players = [{
            "id": player["player"]["id"],
            "winner": player["game_players"]["winner"],
            "name": player["player"]["name"]
            } for player in db(
                db.game_players.game == game["id"]
                ).select(
                    join=db.player.on(db.game_players.player == db.player.id)
                    ).as_list()]
        games[pos]["players"] = players

    return games

def get_recent_tags():
    '''Returns the tags of the last 10 games'''

    db = current.db
    tags = db(
        db.game.playgroup == current.session.playgroup["id"]
        ).select(db.game.tags,
                 orderby=~db.game.timeended,
                 limitby=(0, 10))
    rettags = set()
    for row in tags:
        rettags |= set(row["tags"].split())
    return list(rettags)

def get_ongoing_game(gameid):
    '''Gets the game info'''

    db = current.db
    game_info = db.ongoing_game[gameid].as_dict()
    if game_info['playgroup'] == current.session.playgroup["id"]:
        #select players, join to get name. build a dict for each player this way
        players = [{
            "id": player["player"]["id"],
            "name": player["player"]["name"]
            } for player in db(
                db.ongoing_game_players.ongoing_game == gameid
                ).select(
                    join=db.player.on(
                        db.ongoing_game_players.player == db.player.id
                        ),
                    orderby=db.ongoing_game_players.position
                    ).as_list()]
        game_info["players"] = players
        return game_info
    else:
        return None

def discard_game(gameid):
    '''Discards the game'''

    db = current.db
    game_info = dict(db.ongoing_game[gameid])
    if game_info['playgroup'] == current.session.playgroup["id"]:
        db(db.ongoing_game_players.ongoing_game == gameid).delete()
        db(db.ongoing_game.id == gameid).delete()

def end_game(gameid, wininfo):
    '''Saves the game returns the saved game id'''

    db = current.db
    game_info = get_ongoing_game(gameid)
    result = ""
    players = game_info["players"]
    if game_info != None:
        # Check that we have coherent data
        if "winners" in wininfo:
            # Check per gametype that correct data returned
            if (len(wininfo["winners"]) > 0 and
                    len(wininfo["winners"]) < game_info["playeramount"]):
                #we have one or more winners
                try:
                    winners = [int(w) for w in wininfo["winners"]]
                    for winner in winners:
                        if winner >= game_info["playeramount"] or winner < 0:
                            raise StoreGameException("Invalid winner choice")

                    if game_info["gametype"] == "2-headed":
                        for winner in winners:
                            # Check that all pairs of 2-hg have the same status
                            if winner % 2 == 0 and winner + 1 not in winners:
                                raise StoreGameException("Invalid winner choice")
                            elif winner % 2 == 1 and winner - 1 not in winners:
                                raise StoreGameException("Invalid winner choice")
                    elif game_info["gametype"] == "Emperor":
                        # Check that teams results are consistent
                        t1 = [p for p in winners if p in (0,1,2)]
                        if len(t1) != 0 and len(t1) != 3:
                            raise StoreGameException("Invalid winner choice")
                        t2 = [p for p in winners if p in (3,4,5)]
                        if len(t2) != 0 and len(t2) != 3:
                            raise StoreGameException("Invalid winner choice")
                    elif game_info["gametype"] == "Archenemy":
                        # Check that the AE won or lost alone
                        if 0 in winners and len(winners) != 1:
                            raise StoreGameException("Invalid winner choice")
                        if (0 not in winners and
                                len(winners) != game_info["playeramount"] -1):
                            raise StoreGameException("Invalid winner choice")
                    for winner in winners:
                        players[winner]["winner"] = True
                except ValueError:
                    raise StoreGameException("Invalid winner choice")
                result = "win"
            else:
                # We have a tie
                result = "tie"

            # Check decks
            for i in range(game_info["playeramount"]):
                deckname = game_info["p" + str(i+1) + "deck"]
                if deckname != None and deckname.strip() != "":
                    players[i]["deck"] = deckmgmt.get_deck_id(
                        game_info["players"][i]["id"],
                        deckname)
                else:
                    players[i]["deck"] = None


            #save game info
            saveid = db.game.insert(playgroup=current.session.playgroup["id"],
                                    gametype=game_info["gametype"],
                                    format=game_info["format"],
                                    game=game_info["game"],
                                    onplay=game_info["onplay"],
                                    playeramount=game_info["playeramount"],
                                    result=result,
                                    timestarted=game_info["timestarted"],
                                    timeended=datetime.datetime.now(),
                                    tags=game_info["tags"]).id


            for pos, player in enumerate(game_info["players"]):
                db.game_players.insert(game=saveid,
                                       player=player["id"],
                                       winner=player.get("winner", False),
                                       position=pos+1,
                                       deck=player["deck"])


            db(db.ongoing_game_players.ongoing_game == gameid).delete()
            db(db.ongoing_game.id == gameid).delete()
            return saveid
        else:
            raise StoreGameException("No info about game winners")


def update_game(gameid, update_fields):
    '''Update game state with new fields'''

    db = current.db
    return_data = None
    game_info = db.ongoing_game[gameid]

    if game_info.playgroup == current.session.playgroup["id"]:
        return_data = sanitize_data(update_fields)
        if return_data:
            for field in return_data:
                game_info[field] = return_data[field]
            game_info.update_record()

    return return_data


def sanitize_data(data):
    '''Sanitize the input data to only contain stuff we put in the db want'''
    s_data = {}
    for pair in (("game", "int"),
                 ("onplay", "int"),
                 ("tags", "list:string"),
                 ("p1life", "int"),
                 ("p2life", "int"),
                 ("p3life", "int"),
                 ("p4life", "int"),
                 ("p5life", "int"),
                 ("p6life", "int"),
                 ("p1poison", "int"),
                 ("p2poison", "int"),
                 ("p3poison", "int"),
                 ("p4poison", "int"),
                 ("p5poison", "int"),
                 ("p6poison", "int"),
                 ("p1cmdr", "list:int"),
                 ("p2cmdr", "list:int"),
                 ("p3cmdr", "list:int"),
                 ("p4cmdr", "list:int"),
                 ("p5cmdr", "list:int"),
                 ("p6cmdr", "list:int"),
                 ("p1deck", "string"),
                 ("p2deck", "string"),
                 ("p3deck", "string"),
                 ("p4deck", "string"),
                 ("p5deck", "string"),
                 ("p6deck", "string")):
        try:
            if pair[0] in data:
                if pair[1] == "int":
                    s_data[pair[0]] = int(data[pair[0]])
                elif pair[1] == "string":
                    s_data[pair[0]] = unicode(data[pair[0]])
                elif pair[1] == "list:int":
                    intlist = []
                    for item in data[pair[0]]:
                        intlist.append(int(item))
                    if intlist:
                        s_data[pair[0]] = intlist
                elif pair[1] == "list:string":
                    strlist = []
                    for item in data[pair[0]]:
                        strlist.append(unicode(data[pair[0]]))
                    if intlist:
                        s_data[pair[0]] = strlist

        except (KeyError, TypeError, ValueError):
            pass

    return s_data

def sanitize_filters(filters):
    '''Sanitize the filters to prune bad data'''
    s_filters = {}
    if "min_players" in filters:
        try:
            s_filters["min_players"] = int(filters["min_players"])
        except (TypeError, ValueError, KeyError):
            pass

    if "max_players" in filters:
        max_players = int(filters["max_players"])
        if "min_players" in s_filters:
            if max_players >= s_filters["min_players"]:
                s_filters["max_players"] = max_players
        else:
            s_filters["max_players"] = max_players


    if "after" in filters:
        try:
            s_filters["after"] = datetime.datetime.strptime(
                filters["after"], "%Y-%m-%d")
        except (TypeError, ValueError, KeyError):
            pass

    if "before" in filters:
        try:
            before = datetime.datetime.strptime(filters["before"], "%Y-%m-%d")

            if "after" in s_filters:
                if s_filters["after"] <= before:
                    s_filters["before"] = before
            else:
                s_filters["before"] = before

        except (TypeError, ValueError, KeyError):
            pass

    if "gametype" in filters:
        try:
            filters = [f for f in filters["gametype"] if f in GAMETYPES]
            if len(filters) > 0:
                s_filters["gametype"] = filters

        except TypeError:
            pass

    if "format" in filters:
        try:
            filters = [f for f in filters["format"] if f in FORMATS]
            if len(filters) > 0:
                s_filters["format"] = filters

        except TypeError:
            pass


    if "tags" in filters:
        try:
            tags = [f.encode("utf-8") for f in filters["tags"]]
            if len(tags) > 0:
                s_filters["tags"] = set(tags)

        except TypeError:
            pass

    if "players" in filters:
        try:
            ids = [i["id"] for i in current.session.groupplayers]
            players = [int(p) for p in filters["players"] if int(p) in ids]
            if len(players) > 0:
                s_filters["players"] = set(players)

        except (TypeError, ValueError):
            pass

    if "decks" in filters:
        try:
            ids = [i["id"] for i in deckmgmt.list_decks(player_only=False)]
            decks = [int(d) for d in filters["decks"] if int(d) in ids]
            if len(decks) > 0:
                s_filters["decks"] = set(decks)

        except (TypeError, ValueError):
            pass

    return s_filters


def get_games_for_stats(filters):
    '''Returns games based on filters'''

    db = current.db
    minplayers = 2
    maxplayers = 6
    mintime = datetime.datetime.min
    maxtime = datetime.datetime.now()
    formats = FORMATS
    types = GAMETYPES
    ret_games = []

    s_filters = sanitize_filters(filters)

    if "min_players" in s_filters:
        minplayers = s_filters["min_players"]

    if "max_players" in s_filters:
        maxplayers = s_filters["max_players"]

    if "after" in s_filters:
        mintime = s_filters["after"]

    if "before" in s_filters:
        maxtime = s_filters["before"]

    if "format" in s_filters:
        formats = s_filters["format"]

    if "gametype" in s_filters:
        types = s_filters["gametype"]


    games = db((db.game.playgroup == current.session.playgroup["id"]) &
               (db.game.timeended >= mintime) &
               (db.game.timeended <= maxtime) &
               (db.game.playeramount >= minplayers) &
               (db.game.playeramount <= maxplayers) &
               (db.game.format.belongs(formats)) &
               (db.game.gametype.belongs(types))
              ).select(db.game.id,
                       db.game.playgroup,
                       db.game.gametype,
                       db.game.format,
                       db.game.game,
                       db.game.playeramount,
                       db.game.result,
                       db.game.timeended,
                       db.game.tags).as_list()


    if "tags" in s_filters:
        ngames = [g for g in games if
                  s_filters["tags"].issubset(g["tags"].split())]
        games = ngames

    for agame in games:
        #Filter with players and decks
        gpls = db(db.game_players.game == agame["id"]).select(
            db.game_players.player,
            db.game_players.winner,
            db.game_players.position,
            db.game_players.deck).as_list()


        if "players" in s_filters:
            gplsset = [p["player"] for p in gpls]
            if not s_filters["players"].issubset(gplsset):
                continue

        if "decks" in s_filters:
            deckset = [d["deck"] for d in gpls]
            if not s_filters["decks"].issubset(deckset):
                continue

        for player in gpls:
            player["id"] = player["player"]
            player["name"] = playermgmt.get_playername(player["player"])

        agame["players"] = gpls
        ret_games.append(agame)

    return ret_games

def get_stats(games):
    '''Calculate the stats for the given games'''
    players = {}
    decks = {}

    for agame in games:
        if agame["result"] == "tie":
            tie = True
        else:
            tie = False

        gamedecks = []

        for gpl in agame["players"]:
            if gpl["id"] not in players:
                players[gpl["id"]] = {
                    "name": gpl["name"],
                    "wins": 0,
                    "losses": 0,
                    "ties": 0,
                    "games_played": 0,
                    "goodness": []
                    }

            if gpl["deck"] != None and gpl["deck"] not in gamedecks:
                gamedecks.append(gpl["deck"])

            players[gpl["id"]]["games_played"] += 1

            if tie:
                players[gpl["id"]]["ties"] += 1
            elif gpl["winner"]:
                players[gpl["id"]]["wins"] += 1
            else:
                players[gpl["id"]]["losses"] += 1

            # Goodness of the game
            goodness = 0
            if tie:
                goodness = 50
            elif agame["gametype"] == "Star":
                if gpl["winner"]:
                    #count winners
                    winner = 0
                    for apl in agame["players"]:
                        if apl["winner"]:
                            winner += 1
                    if winner == 1:
                        goodness = 100
                    else:
                        goodness = 80
            elif gpl["winner"]:
                goodness = 100
            elif agame["gametype"] == "Basic":
                #Loser in a multiplayer game, be less harsh
                goodness = 50 - 50 / (int(agame["playeramount"]) - 1)


            players[gpl["player"]]["goodness"].append(goodness)


        for deck in agame["players"]:
            if deck["deck"] == None:
                continue

            if deck["deck"] not in decks:
                decks[deck["deck"]] = {
                    "name": deckmgmt.get_deckname(deck["deck"]),
                    "wins": 0,
                    "losses": 0,
                    "ties": 0,
                    "games_played": 0,
                    "matchups": {}
                    }

            for matchup in gamedecks:
                if matchup != deck["deck"]:
                    if (matchup not in decks[deck["deck"]]["matchups"] and
                            matchup != None):
                        decks[deck["deck"]]["matchups"][matchup] = {
                            "oname": deckmgmt.get_deckname(matchup),
                            "wins": 0,
                            "winsps": 0,
                            "losses": 0,
                            "lossesps": 0,
                            "ties": 0,
                            "tiesps": 0,
                            "games_played": 0,
                            }



            decks[deck["deck"]]["games_played"] += 1
            for matchup in gamedecks:
                if matchup != deck["deck"] and matchup != None:
                    decks[deck["deck"]]["matchups"][matchup]["games_played"] += 1

            if tie:
                decks[deck["deck"]]["ties"] += 1
                for matchup in gamedecks:
                    if matchup != deck["deck"] and matchup != None:
                        decks[deck["deck"]]["matchups"][matchup]["ties"] += 1
                        if agame["game"] != 1:
                            decks[deck["deck"]]["matchups"][matchup]["tiesps"] += 1
            elif deck["winner"]:
                decks[deck["deck"]]["wins"] += 1
                for matchup in gamedecks:
                    if matchup != deck["deck"] and matchup != None:
                        decks[deck["deck"]]["matchups"][matchup]["wins"] += 1
                        if agame["game"] != 1:
                            decks[deck["deck"]]["matchups"][matchup]["winsps"] += 1
            else:
                decks[deck["deck"]]["losses"] += 1
                for matchup in gamedecks:
                    if matchup != deck["deck"] and matchup != None:
                        decks[deck["deck"]]["matchups"][matchup]["losses"] += 1
                        if agame["game"] != 1:
                            decks[deck["deck"]]["matchups"][matchup]["lossesps"] += 1

    for player in players.keys():
        #Calculate goodness
        players[player]["goodness"] = float(sum(players[player]["goodness"]) /
                                            len(players[player]["goodness"]))
    return {"players": players, "decks": decks}



class NewGameException(Exception):
    "Exception for invalid data for new game."
    def __init__(self, message=None):
        Exception.__init__(self)
        self.message = message

class StoreGameException(Exception):
    "Exception for invalid data when storing game."
    def __init__(self, message=None):
        Exception.__init__(self)
        self.message = message

