"""This backend module handles all deck related actions"""
from gluon import current

def list_decks(player_only=True):
    '''Lists the decks for player or playgroup'''

    db = current.db
    if player_only:
        decks = db(
            db.deck.owner == current.session.playerid
            ).select(db.deck.name, db.deck.id).as_list()
    else:
        decks = db(
            db.groupplayer.playgroup == current.session.playgroup["id"]
            ).select(db.deck.name, db.deck.id,
                     join=db.deck.on(
                         db.deck.owner == db.groupplayer.player
                         )).as_list()

    return decks

def get_deckname(id):
    '''Returns the deck name for the id'''

    db = current.db
    deck = db(db.deck.id == id).select(cache=(current.cache.ram, 60)).first()
    if deck != None:
        return deck.name
    else:
        return ""

def get_deck_id(player, deckname):
    '''Returns the id for the deck
         If the deckname exists for the player, that id is returned
         If the deckname exists in the playgroup, that id is returned
         else a deck with this name is added to the player's decklist'''

    db = current.db
    result = db(
        (db.deck.owner == player) &
        (db.deck.name == deckname)
        ).select(db.deck.id).first()
    if result != None:
        # We found deck
        return result.id

    else:
        # Look for friends' decks
        for friend in current.session.groupplayers:
            result = db(
                (db.deck.owner == friend["id"]) &
                (db.deck.name == deckname)
                ).select(db.deck.id).first()
            if result != None:
                # We found deck
                return result.id

        # create new deck
        return db.deck.insert(owner=player, name=deckname)

def merge_decks(sourceid, targetid):
    '''Merges two decks.
    Points all previous player deck info to the new deck
    and remove the old deck'''

    db = current.db
    sourcedeck = db(
        (db.deck.id == sourceid) &
        (db.deck.owner == current.session.playerid)
        ).select(db.deck.id).first()
    targetdeck = db(
        (db.deck.id == targetid) &
        (db.deck.owner == current.session.playerid)
        ).select(db.deck.id).first()
    if sourcedeck != None and targetdeck != None:
        db(db.game_players.deck == sourcedeck.id).update(deck=targetdeck.id)
        db(db.deck.id == sourcedeck.id).delete()
    else:
        raise ValueError
