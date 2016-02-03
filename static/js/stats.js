String.prototype.trim = function() {
   return this.replace(/^\s+|\s+$/g,"");
}

function clear_data() {
  jQuery("div#playerprints").html("");
  jQuery("div#deckprints").html("");
  jQuery("div#gamelistdiv").html("");
}

function print_data(data) {
  if (data["games"].length == 0) {
    jQuery("div#playerprints").html("<h2>No results</h2>");
    jQuery("div#deckprints").html("<h2>No results</h2>");
  }
  else {
    print_games(data["games"], jQuery("div#gamelistdiv"));
    print_playerstats(data);
    print_deckstats(data);
  }
}


function print_playerstats(data) {
  var playerids = Object.keys(data["players"]);
  var players = [];
  var winpr = [];
  var losspr = [];
  var tiepr = [];
  var goodness = [];
  var games = [];

  jQuery("div#playerprints").append("<canvas id='playersummary' width='720' height='400'></canvas>");
  jQuery("div#playerprints").append("<img src='../static/images/legend.png'>");

  for ( i=0 ; i < playerids.length ; i++ ){
    pid = playerids[i];
    players.push(data["players"][pid]["name"]);
    winpr.push(100 * data["players"][pid]["wins"]/data["players"][pid]["games_played"]);
    losspr.push(100 * data["players"][pid]["losses"]/data["players"][pid]["games_played"]);
    tiepr.push(100 * data["players"][pid]["ties"]/data["players"][pid]["games_played"]);
    goodness.push(data["players"][pid]["goodness"]);
    games.push(data["players"][pid]["games"]);
    
    jQuery("div#playerprints").append("<div class='playerdoughnut'><div class='name'>" + data["players"][pid]["name"]
        + "</div><canvas id='player-" + pid
        + "'' height='200' width='200'></canvas></div>")
    var pctx = jQuery("#player-" + pid).get(0).getContext("2d");
    new Chart(pctx).Doughnut(
      [
        {
            value: data["players"][pid]["wins"],
            color:"#1ABB1A",
            highlight: "#FF5A5E",
            label: "Wins"
        },
        {
            value: data["players"][pid]["losses"],
            color: "#DD3A3A",
            highlight: "#5AD3D1",
            label: "Losses"
        },
        {
            value: data["players"][pid]["ties"],
            color: "#969696",
            highlight: "#FFC870",
            label: "Ties"
        }
      ], {});    
  }

  var chartdata = {
    labels: players,
    datasets: [
        {
            label: "Goodness",
            data: goodness,
            fillColor: "rgba(255,219,77,1)"
        },
        {
            label: "Win %",
            data: winpr,
            fillColor: "rgba(26,187,26,1)"
        },
        {
            label: "Loss %",
            data: losspr,
            fillColor: "rgba(221,58,58,1)"
        },
        {
            label: "Tie %",
            data: tiepr,
            fillColor: "rgba(150,150,150,1)"
        }
    ]
  }
  var ctx = jQuery("#playersummary").get(0).getContext("2d");
  new Chart(ctx).Bar(chartdata, {barValueSpacing : 10,});

};

function print_deckstats(data) {
  var deckids = Object.keys(data["decks"]);

  for ( i=0 ; i < deckids.length ; i++ ){
    did = deckids[i]; 
    
    jQuery("div#deckprints").append("<div class='deckdoughnut' id='ddiv-" + did + "'>" 
        + "<div class='toggle plus togglematchup' id='show-matchup-" + did + "'></div>"
        + "<div class='name'>" + data["decks"][did]["name"] + "</div>"
        + "<div class='matchup'><canvas id='deck-" + did
        + "' height='200' width='200'></canvas></div></div>");
    var pctx = jQuery("#deck-" + did).get(0).getContext("2d");
    new Chart(pctx).Doughnut(
      [
        {
            value: data["decks"][did]["wins"],
            color:"#1ABB1A",
            highlight: "#FF5A5E",
            label: "Wins"
        },
        {
            value: data["decks"][did]["losses"],
            color: "#DD3A3A",
            highlight: "#5AD3D1",
            label: "Losses"
        },
        {
            value: data["decks"][did]["ties"],
            color: "#969696",
            highlight: "#FFC870",
            label: "Ties"
        }
      ], {});    
    
    // Print matchups, but don't show them by default
    jQuery("div#ddiv-" + did).append("<div id='matchup-" + did + "' hidden='true' class='matchups-d'></div>");
    matchupids = Object.keys(data["decks"][did]["matchups"]);
    for ( d=0 ; d < matchupids.length ; d++ ){
      mid = matchupids[d];
      jQuery("div#matchup-" + did).append("<div id='matchup-" + did + "-"
          + mid + "' class='mathcup'><div>Against " + data["decks"][did]["matchups"][mid]["oname"]
          + "</div><div class='float'><div>All games</div><canvas id='deck-" + did + "-" + mid
          + "' height='200' width='200'></canvas></div><div class='float'><div>Post sideboarding</div>"
          + "<canvas id='deck-" + did + "-" + mid + "-ps"
          + "' height='200' width='200'></canvas></div></div>");
      var pctx = jQuery("#deck-" + did + "-" + mid).get(0).getContext("2d");
      new Chart(pctx).Doughnut(
        [
          {
              value: data["decks"][did]["matchups"][mid]["wins"],
              color:"#1ABB1A",
              highlight: "#FF5A5E",
              label: "Wins"
          },
          {
              value: data["decks"][did]["matchups"][mid]["losses"],
              color: "#DD3A3A",
              highlight: "#5AD3D1",
              label: "Losses"
          },
          {
              value: data["decks"][did]["matchups"][mid]["ties"],
              color: "#969696",
              highlight: "#FFC870",
              label: "Ties"
          }
        ], {});
      var pctx = jQuery("#deck-" + did + "-" + mid + "-ps").get(0).getContext("2d");
      new Chart(pctx).Doughnut(
        [
          {
              value: data["decks"][did]["matchups"][mid]["winsps"],
              color:"#1ABB1A",
              highlight: "#FF5A5E",
              label: "Wins post sideboard"
          },
          {
              value: data["decks"][did]["matchups"][mid]["lossesps"],
              color: "#DD3A3A",
              highlight: "#5AD3D1",
              label: "Losses post sideboard"
          },
          {
              value: data["decks"][did]["matchups"][mid]["tiesps"],
              color: "#969696",
              highlight: "#FFC870",
              label: "Ties post sideboard"
          }
        ], {});    
    }    

  }
}


function toggle_search() {
  jQuery("div#filterdiv").slideToggle();
  jQuery("div#toggle-search").toggleClass("plus");
  jQuery("div#toggle-search").toggleClass("minus");
}

function toggle_gamelist() {
  jQuery("div#gamelistdiv").slideToggle();
  jQuery("div#toggle-gamelist").toggleClass("plus");
  jQuery("div#toggle-gamelist").toggleClass("minus");
}

function toggle_matchup(e) {
  mclass = "matchup-" + jQuery(e.target).attr("id").split("-")[2];
  jQuery("div#" + mclass).slideToggle();
  jQuery(e.target).toggleClass("plus");
  jQuery(e.target).toggleClass("minus");
}

function show_decks(e) {
  jQuery("div#decktab").addClass("activetab");
  jQuery("div#playertab").removeClass("activetab");
  jQuery("div#playerprints").hide();
  jQuery("div#deckprints").show();
}

function show_players(e) {
  jQuery("div#playertab").addClass("activetab");
  jQuery("div#decktab").removeClass("activetab");
  jQuery("div#playerprints").show();
  jQuery("div#deckprints").hide();
}

function filter_games() {
    var players = null;
    var decks = null;
    var format = [];
    var gametype = [];
    var min_players = null;
    var max_players = null;
    var after = null;
    var before = null;
    var tags = null;

    players = jQuery("select#playerselect").val() || null;
    decks = jQuery("select#deckselect").val() || null;
    jQuery("input[name='format']:checked").each(function() {
        format.push(this.value)
    });
    jQuery("input[name='gametype']:checked").each(function() {
        gametype.push(this.value)
    });

    min_players = jQuery("select#minplayerselect").val() || null;
    max_players = jQuery("select#maxplayerselect").val() || null;

    after = jQuery("input#datestart").val() || null;
    before = jQuery("input#dateend").val() || null;
    if (jQuery("input#tags").val().trim() != "")  
      tags = jQuery("input#tags").val().trim().replace(",", " ").split(" ") || null;

    filters = new Object();
    if (players != null)
        filters["players"] = players;
    if (decks != null)
        filters["decks"] = decks;
    if (format.length > 0)
        filters["format"] = format;
    if (gametype.length > 0)
        filters["gametype"] = gametype;
    if (min_players != null)
        filters["min_players"] = min_players;
    if (max_players != null)
        filters["max_players"] = max_players;
    if (after != null)
        filters["after"] = after;
    if (before != null)
        filters["before"] = before;
    if (tags != null)
        filters["tags"] = tags;

    $.ajax({  
       url: app_prefix + 'stats/filter.json',
       type:'POST',  
       dataType: 'Json',

       data: JSON.stringify(filters),
       
      success: function(data) {
        clear_data();
        print_data(data);
        toggle_search();
      }    
    });   
}

jQuery(document).ready(function() {
  jQuery("button#filter").bind("click", filter_games);
  jQuery("#datestart").datepicker();
  jQuery("#dateend").datepicker();
  jQuery("#datestart").datepicker("option", "dateFormat", "yy-mm-dd");
  jQuery("#dateend").datepicker("option", "dateFormat", "yy-mm-dd");
  jQuery("div#toggle-gamelist").bind("click", toggle_gamelist);
  jQuery("div#toggle-search").bind("click", toggle_search);
  jQuery("div#decktab").bind("click", show_decks);
  jQuery("div#playertab").bind("click", show_players);
  jQuery(document).on('click', 'div.togglematchup', toggle_matchup);
});