import playermgmt
import game


@auth.requires_login()
def newgame():
    playermgmt.ensure_session_vars(auth)

    if 'copy' in request.vars:
        #copy a previous game
        try:
            game_id = game.create_game(copyfrom=int(request.vars["copy"]))
            redirect(URL('ingame', 'ingame', vars=dict(game_id=game_id)))
        except (ValueError, game.NewGameException):
            pass


    formgame=SQLFORM.factory(
        Field("gametype",
              requires=IS_IN_SET(game.GAMETYPES,
              zero=None)),
        Field("players",
              requires=IS_IN_SET(["2","3", "4", "5", "6"],
              zero=None)),
        Field("format",
              requires=IS_IN_SET(game.FORMATS,
              zero=None)),
        Field("tags"),
        Field("player1"),
        Field("player2"),
        Field("player3"),
        Field("player4"),
        Field("player5"),
        Field("player6"),
        formstyle="divs",
        submit_button = 'Start')


    
    if formgame.process().accepted:
        try:
            playeramount = int(formgame.vars.players)
            players = []

            if (playeramount not in
                    game.PLAYERAMOUNTS.get(formgame.vars.gametype, [])):
                raise game.NewGameException(
                    "Wrong amount of players for the format")

            for i in range(1,playeramount+1):
                try:
                    playerid = int(formgame.vars["player" + str(i)])
                except ValueError:
                    raise game.NewGameException("Invalid player id")
                if playerid == None:
                    raise game.NewGameException(
                        "Please insert player " + str(i))
                else:
                    addplayer = [player for player in
                                 session.groupplayers if
                                 player["id"] == playerid]
                    if len(addplayer) != 0:
                        players.append(addplayer[0])
                    elif playerid == session.guestplayer["id"]:
                        players.append(session.guestplayer)
                    else:
                        raise game.NewGameException("Player not found")

            gamedata = dict(formgame.vars)
            tags = gamedata["tags"]
            gamedata["tags"] = tags.replace(",", " ").strip()
            gamedata["players"] = players
            gamedata["playeramount"] = playeramount

            game_id = game.create_game(gamedata)
            redirect(URL('ingame', 'ingame', vars=dict(game_id=game_id)))
        except game.NewGameException as nge:
            if nge.message:
                response.flash = nge.message



    elif formgame.errors:
        response.flash = 'form has errors'

    return dict(formgame=formgame,
                playerlist=session.groupplayers,
                guestplayer=session.guestplayer,
                tags=game.get_recent_tags())
