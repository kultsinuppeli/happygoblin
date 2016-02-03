function print_games(games, parent) {
    table = $('<table class="table-striped table-responsive"><tr><th>Ended</th><th>Players</th><th>Type</th><th>Tags</th></table>');
        

    for (i = 0 ; i < games.length ; i++) {
        winners = '';
        losers = '';

        for (d = 0 ; d < games[i]["players"].length ; d++) {
            if ( games[i]["players"][d]["winner"] ) 
                winners +=  '<span class="winner">' + 
                            games[i]["players"][d]["name"] + 
                            '</span> ';
            else
                losers += '<span class="loser">' + 
                          games[i]["players"][d]["name"] + 
                          '</span> ';

        }

        gametime = get_local_date(games[i]["timeended"]);

        row = $('<tr id="' + games[i]["id"] + '">' +
                '<td class="game_time"><time class="timeago" datetime="' + gametime + '"></time></td>' +
                '<td class="game_players">' + winners + losers + '</td>' +
                '<td class="game_type">' + games[i]["gametype"] + '</td>' +
                '<td class="game_tags">' + games[i]["tags"] + '</td>' +
                '</tr>');

        table.append(row);
    }
    parent.html(table);
    $("time.timeago").timeago();

}

function print_ongoing_games(games, parent) {
    table = $('<table class="table-striped table-responsive"><tr><th>Started</th><th>Players</th><th>Type</th><th>Tags</th><th></th></table>');
        

    for (i = 0 ; i < games.length ; i++) {
        losers = '';

        for (d = 0 ; d < games[i]["players"].length ; d++) {
            losers += '<span class="winner">' + 
                      games[i]["players"][d]["name"] + 
                      '</span> ';

        }
        gametime = get_local_date(games[i]["timestarted"]);

        row = $('<tr id="' + games[i]["id"] + '">' +
                '<td class="game_time"><time class="timeago" datetime="' + gametime + '"></time></td>' +
                '<td class="game_players">' + losers + '</td>' +
                '<td class="game_type">' + games[i]["gametype"] + '</td>' +
                '<td class="game_tags">' + games[i]["tags"] + '</td>' +
                '<td><button onclick="window.location.href=\'' + app_prefix + 'ingame/ingame?game_id=' +  games[i]["id"] + '\'">Go</button></td>' + 
                '</tr>');

        table.append(row);
    }
    parent.html(table);
    $("time.timeago").timeago();

}

function get_local_date(datestring) {
    tzoffset = new Date().getTimezoneOffset();
    years = datestring.split(" ")[0].split("-")[0];
    // Because JavaScript is being an idiot
    months = datestring.split(" ")[0].split("-")[1] - 1;
    days = datestring.split(" ")[0].split("-")[2];
    hours = datestring.split(" ")[1].split(":")[0];
    minutes = parseInt(datestring.split(" ")[1].split(":")[1]) - parseInt(tzoffset);
    return new Date(years, months, days, hours, minutes).toISOString();
}