function flip_p1() {
  var new_transform;
  if (p1_flipped) {
    new_transform = "translate(-50%, 0)"
  }
  else {
    new_transform = "translate(-50%, 0) rotate(180deg)"
  }
  p1_flipped = !p1_flipped;
  jQuery("div#ig-p1Basic2p").css("transform", new_transform);


}

function mod_life() {
  var id = this.id.split("-");
  var what = id[0];
  var amount = id[1];
  var cur_amount=parseInt(jQuery("div#" + what).html());
  switch (amount) {
    case "minus5":
      cur_amount -= 5;
      break;
    case "minus1":
      cur_amount -= 1;
      break;
    case "plus1":
      cur_amount +=1;
      break;
    case "plus5":
      cur_amount +=5;
      break;
  }
  jQuery("div#" + what).html(cur_amount);
  update_info[what] = cur_amount;

  // Set a 1 second timar to update the server
  // If a timer exists, reset the timer
  if (timeout_id != 0) {
    clearTimeout(timeout_id);
    timeout_id = 0;
  }
  timeout_id = setTimeout (update_server, 1000 );
}

function mod_deck() {
  
  if (this.id.search("2headed") != -1 ) {
    update_info[this.id.split("-")[0]] = this.value;
  }
  else {
    update_info[this.id] = this.value;
  }

  // Set a 1 second timar to update the server
  // If a timer exists, reset the timer
  if (timeout_id != 0) {
    clearTimeout(timeout_id);
    timeout_id = 0;
  }
  timeout_id = setTimeout (update_server, 1000 );
}

function update_server(){
  $.ajax({  
         url: app_prefix + 'ingame/update_game_info.json?game_id='+game_id,  
         type:'POST',  
         dataType: 'Json',

         data: JSON.stringify(update_info),

         success: function(data) {  
         }  
     });  
  
  update_info = new Object();

}

function receive_updates(unparsed) {
  try {
    data = JSON.parse(unparsed.data);
  }
  catch (e) {
    return;
  }
  if ("gameFinished" in data) {
    // Finish game dialog
    if (!ignore_savemessage) {
      bootbox.dialog({
                message: "The game has ended",
                title: "Game stored",
                closeButton: false,
                buttons: {
                  success: {
                    label: "Front page",
                    className: "btn-primary",
                    callback: function() {
                      window.location = "../default/index";
                    }
                  }
                }});
    }
  }
  else {
    for (var key in data) {
      if (key.search("deck") != -1) {
        if (gametype == "2-headed" &&
            (key == "p2deck" || key == "p4deck" || key == "p6deck")) {
          jQuery("input#" + key + "-2headed").val(data[key]);
        }
        else {
            jQuery("input#" + key).val(data[key]);
        }
      }
      else {
        jQuery("div#" + key).html(data[key]);  
      }
    }
  }

}

function set_players(data) {
  var pdiv = jQuery("DIV#players")[0];
  var counter = 0;

  jQuery("div#players").addClass("c" + gametype + players +"p");

  if (gametype != "2-headed") {
    jQuery("input.deckname-2-headed").hide();
    jQuery("p.playername-2-headed").hide();
  }
  else {
    jQuery("input.deckname-2-headed").show();
    jQuery("p.playername-2-headed").show();
  }

  for (counter=0; counter<6; counter++) {
    pdiv.children[counter].id="ig-p"+ (counter+1) + gametype + players +"p";
    if (gametype != "2-headed") {
      if (counter < players) {
        //enable visible players
        pdiv.children[counter].hidden=false;
        jQuery("p#name-p" + (counter+1)).html(data["players"][counter].name);
        jQuery("input#p" + (counter+1) + "deck").attr("placeholder", "Deck " + data["players"][counter].name);
        jQuery("div#p" + (counter+1) + "life").html(data["p" + (counter+1) + "life"]);
        if (data["p" + (counter +1) + "deck"] != null && data["p" + (counter +1) + "deck"] != "")
          var a = jQuery("input#p" + (counter+1) + "deck");
          jQuery("input#p" + (counter+1) + "deck" ).val(data["p" + (counter+1) + "deck"]);
      }

      else
        pdiv.children[counter].hidden=true;


    }
    else {
      // In 2hg only enable every other playerbox
      if (counter == 0 || counter == 2 || (counter == 4 && players == 6)) {
        pdiv.children[counter].hidden=false;
        jQuery("p#name-p" + (counter+1)).html(data["players"][counter].name);
        jQuery("input#p" + (counter+1) + "deck").attr("placeholder", "Deck " + data["players"][counter].name);
        jQuery("p#name-p" + (counter+2) + "-2-headed").html(data["players"][counter+1].name);
        jQuery("input#p" + (counter+2) + "deck-2headed").attr("placeholder", "Deck " + data["players"][counter+1].name);
        jQuery("div#p" + (counter+1) + "life").html(data["p" + (counter+1) + "life"]);
        if (data["p" + (counter +1) + "deck"] != null && data["p" + (counter +1) + "deck"] != "")
          jQuery("input#p" + (counter +1) + "deck").val(data["p" + (counter+1) + "deck"]);
        
        if (data["p" + (counter +2) + "deck"] != null && data["p" + (counter +2) + "deck"] != "")
          jQuery("input#p" + (counter+2) + "deck-2headed").val(data["p" + (counter+2) + "deck"]);
        

      }
      else
        pdiv.children[counter].hidden=true;

    }

  }
}

function toggle_win() {
  var pdiv = jQuery("DIV#players")[0];
  switch (gametype) {
    case "Emperor":
      var startid = 0;
      if (this.id[4] >=4 ) 
        startid = 3;

      if (this.className ==  "player-game lost") {
        pdiv.children[startid].className = "player-game won";
        pdiv.children[startid+1].className = "player-game won";
        pdiv.children[startid+2].className = "player-game won";
      }
      else {
        pdiv.children[startid].className = "player-game lost";
        pdiv.children[startid+1].className = "player-game lost";
        pdiv.children[startid+2].className = "player-game lost";
      }
      break;
    case "Archenemy":
      if (this.id[4] == 1) {
        if (this.className ==  "player-game lost") 
          this.className = "player-game won";
        else
          this.className = "player-game lost";
      } else {
        for (counter=1; counter<players; counter++) {  
          if (pdiv.children[counter].className ==  "player-game lost") 
            pdiv.children[counter].className = "player-game won";
          else
            pdiv.children[counter].className = "player-game lost";
        }
      }
      break;
    default:
      if (this.className ==  "player-game lost") 
        this.className = "player-game won";
      else
        this.className = "player-game lost";
      break;
  }
  
}

function finish_game() {
  var pdiv = jQuery("DIV#players")[0];
  var counter = 0;
  jQuery("div#message").html("Select winner");
  jQuery("button#ig-finish").html("Done!");
  jQuery("button#ig-finish").off("click");
  jQuery("button#ig-finish").click(save_result);

  switch (gametype) {
    case "Emperor":
      for (counter=0; counter<players; counter+=3) {
        var life = parseInt(jQuery("div#p" + pdiv.children[counter].id[4] + "life").html());
        var poison = parseInt(jQuery("div#p" + pdiv.children[counter].id[4] + "poison").html());
        
        if ( life <= 0 || poison >= 10 ) {
          pdiv.children[counter].className = "player-game lost";
          pdiv.children[counter+1].className = "player-game lost";
          pdiv.children[counter+2].className = "player-game lost";
        } else {
          pdiv.children[counter].className = "player-game won";
          pdiv.children[counter+1].className = "player-game won";
          pdiv.children[counter+2].className = "player-game won";
        }
        jQuery("div#" + pdiv.children[counter].id).click(toggle_win);
        jQuery("div#" + pdiv.children[counter+1].id).click(toggle_win);
        jQuery("div#" + pdiv.children[counter+2].id).click(toggle_win);

      }
      break;
    case "Archenemy":
      var life = parseInt(jQuery("div#p1life").html());
      var poison = parseInt(jQuery("div#p1poison").html());
      if ( life <= 0 || poison >= 10 ) {
        pdiv.children[0].className = "player-game lost";
      } else {
        pdiv.children[0].className = "player-game won";
      }
      jQuery("div#" + pdiv.children[counter].id).click(toggle_win);

      for (counter=1; counter<players; counter++) {  
        jQuery("div#" + pdiv.children[counter].id).click(toggle_win);
        pdiv.children[counter].className = "player-game won";
      }
      break;
    default:
      for (counter=0; counter<players; counter++) {
        var life = parseInt(jQuery("div#p" + pdiv.children[counter].id[4] + "life").html());
        var poison = parseInt(jQuery("div#p" + pdiv.children[counter].id[4] + "poison").html());
        
        if ( life <= 0 || poison >= 10 ) {
          pdiv.children[counter].className = "player-game lost";
        } else {
          pdiv.children[counter].className = "player-game won";
        }
        jQuery("div#" + pdiv.children[counter].id).click(toggle_win);
   
      }
       break;

  }

}

function save_result() {
  var pdiv = jQuery("DIV#players")[0];
  var winneramount = 0;
  var gameresult = new Object();
  gameresult["winners"] = [];
  var message;
  ignore_savemessage = true;
  
  for (counter=0; counter<players; counter++) {
    if (pdiv.children[counter].hidden == false ) {
      if (pdiv.children[counter].className ==  "player-game won") {
        winneramount += 1;
        gameresult["winners"].push(counter);
        if (gametype == "2-headed") {
          winneramount += 1;
          counter += 1;
          gameresult["winners"].push(counter);
        }      
      }
    }
  } 
  if (winneramount >= players || winneramount == 0) {
    // A Tie
    gameresult["winners"] = [];
  }

  var bbdialog = {
              message: "The game has ended",
              title: "Game stored",
              closeButton: false,
              buttons: {
                success: {
                  label: "Front page",
                  className: "btn-primary",
                  callback: function() {
                    window.location = "../default/index";
                  }
                },
                negame: {
                  label: "New game",
                  className: "btn-primary",
                  callback: function() {
                    window.location = "../newgame/newgame";
                  }
                },
              }
            }
  if (game <= 2) {
    bbdialog.buttons.rematch = {
          label: "To game " + (game+1),
          className: "btn-primary",
          callback: function() {
            window.location = "../newgame/newgame?copy=" + saveid;
          }
        }


  }
  $.ajax({  
         url: app_prefix + 'ingame/end_game.json?game_id='+game_id,  
         type:'POST',  
         dataType: 'Json',

         data: JSON.stringify(gameresult),

         success: function(data) {  
            if ("saveid" in data) {
              saveid = data["saveid"];
            }
            bootbox.dialog(bbdialog);
        }    
  }); 

}

function discard_game() {
  bootbox.confirm("Discard this game?", function(result) {
    if (result == true) {
      $.getJSON('discard_game.json?game_id='+game_id, function(data) {
        window.location = app_prefix + "default/index";
      });

    }
    
  }); 
}

jQuery(document).ready(function() {
  $.getJSON('get_game_state.json?game_id='+game_id, function(data) {
    var counter = 0;
    gametype = data["gametype"];
    last_update_id = data["last_update_id"];
    game = data["game"];
    update_info = new Object();
    players = data["playeramount"]
    ignore_savemessage = false;
    saveid = 0;
    set_players(data);
    jQuery("button.plus1").click(mod_life);
    jQuery("button.plus5").click(mod_life);
    jQuery("button.minus1").click(mod_life);
    jQuery("button.minus5").click(mod_life);
    jQuery("button#ig-finish").click(finish_game);
    jQuery("button#ig-discard").click(discard_game);
    if ( (gametype == "Basic" && players == 2) ||
         (gametype == "2-headed" && players == 4)) {
      // Modify classes for large view
      jQuery("button#ig-flip").click(flip_p1);
      jQuery("button#ig-flip").show();
      p1_flipped = false;

      jQuery("button.plus1").addClass("plus1-large");
      jQuery("button.plus5").addClass("plus5-large");
      jQuery("button.minus1").addClass("minus1-large");
      jQuery("button.minus5").addClass("minus5-large");
      jQuery("div.dmgtype").addClass("dmgtype-large");
      jQuery("p.playername-2-headed").addClass("playername-2-headed-large");
      jQuery("input.deckname-2-headed").addClass("deckname-2-headed-large");
    }    

  });
  
  $.getJSON('get_deck_names.json', function(data) {
    jQuery("input.deckname, input.deckname-2-headed").autocomplete({
      source: data["decks"],
      select: function( event, ui ) {
        this.value = ui.item.value;
        update_info[this.id] = this.value;

        // Set a 1 second timar to update the server
        // If a timer exists, reset the timer
        if (timeout_id != 0) {
          clearTimeout(timeout_id);
          timeout_id = 0;
        }
        timeout_id = setTimeout (update_server, 1000 ); 
      }
    });
    jQuery("input.deckname, input.deckname-2-headed").bind("focusout", mod_deck);
  });

  if(!web2py_websocket("ws://" + websocket_server + 'realtime/'+ game_id ,receive_updates))
     alert("html5 websocket not supported by your browser");

});