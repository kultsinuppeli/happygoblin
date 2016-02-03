function enablePlayerselect(amounts)
{
  // Change amount of players one can select for this gametype
  // Return the amount of players selected
  var counter = 0;
  var now_selected = parseInt(jQuery("#no_table_players")[0].options[jQuery("#no_table_players")[0].selectedIndex].value);
  jQuery("#no_table_players")[0].options.length=0;
  var found_same = false;

  for (counter=0; counter<amounts.length; counter++) {

    if (amounts[counter] == now_selected) {
      jQuery("#no_table_players")[0].options[counter] = new Option(amounts[counter], amounts[counter], false, true);
      found_same = true;
    }
    else
      jQuery("#no_table_players")[0].options[counter] = new Option(amounts[counter], amounts[counter], false, false);
  }
  if (!found_same) {
    jQuery("#no_table_players")[0].options[0].selected=true;
    now_selected = parseInt(jQuery("#no_table_players")[0].options[0].value);
  }


  return now_selected;
}

function movePlayer(newparent, moveid) {

  var newslot = false;
  var newid = false;
  var oldslot = false;
  var oldid = guestplayer;
  var oldparent = jQuery("#"+moveid).parent();

  if (oldparent[0].id == newparent[0].id) {
    //don't do anything if we drag to the same
    return false;
  }

  if (newparent[0].id.substring(0, 10) == "playerslot") { 
    newslot = newparent[0].id.charAt(10);
    newid = moveid.split("-")[1];
  }
  if (oldparent[0].id.substring(0, 10) == "playerslot") { 
    oldslot = oldparent[0].id.charAt(10);
  }
  var moveobject = jQuery("#"+moveid).detach();
  var movesign = jQuery(moveobject[0].children[0]);

  // Moving to a playerslot
  if (newparent[0].id.substring(0, 10) == "playerslot") {
    if ( newparent[0].children.length == 1 ) {
      // Switch these
      oldid = jQuery(newparent[0].children[0])[0].id.split("-")[1];
      var switchobject = jQuery(newparent[0].children[0]).detach();
      oldparent.append(switchobject);
      if (oldslot == false) {
        // Switching back to pool
        jQuery(switchobject[0].children[0]).removeClass('minus');
        jQuery(switchobject[0].children[0]).addClass('plus');
      }
    } else {
      newparent[0].innerHTML = "";
      if (oldparent[0].id.substring(0, 10) == "playerslot") {
        oldparent[0].innerHTML = "Guest " + getSlotName(oldslot);
        
      }

    }
    newparent.append(moveobject);

    if ( newslot != false )
      // If we moved to a playerslot
      jQuery("input#player" + newslot)[0].value=newid;

    if ( oldslot != false ) {
      // If we moved from a playerslot
      jQuery("input#player" + oldslot)[0].value=oldid;
    }
    movesign.removeClass('plus');
    movesign.addClass('minus');

  } else {
    // Move back to pool
    newparent.append(moveobject);
    oldparent[0].innerHTML = "Guest " + getSlotName(oldslot);
    if ( oldslot != false ) {
      jQuery("input#player" + oldslot)[0].value=oldid;
    }
    movesign.removeClass('minus');
    movesign.addClass('plus');
  }
  return true;
}

function quickAdd(player) {
  if (justmoved)
    return;

  if (jQuery(this).hasClass("plus")) {
    var counter;
    for (counter = 1; counter <= players ; counter++) {
      if (jQuery("input#player" + counter)[0].value == guestplayer) {
        movePlayer(jQuery("div#playerslot"+counter), jQuery(this).parent()[0].id);
        return;
      }
    }
  } else {
    movePlayer(jQuery("div#playerlist"), jQuery(this).parent()[0].id);
  }
}

function getSlotName(slot) {
  var type = jQuery("#no_table_gametype")[0].options[jQuery("#no_table_gametype")[0].selectedIndex];
  if (type.value == "Basic") {
    return "(Player " + slot + ")";
  }
  else if (type.value == "2-headed") {
    team = Math.ceil((slot / 2));
    player = slot - 2 * (team -1);  
    return "(Team " + team + " Player" + player + ")"
  }
  else if (type.value == "Star") {
    return "(Player " + slot + ")"
  }
  else if (type.value == "Emperor") {
    if (slot == 1)
      return "(Team 1 Emperor)"
    if (slot == 6)
      return "(Team 2 Emperor)"
    if (slot == 2 || slot == 3)
      return "(Team 1 General " + (slot - 1) + ")" 
    if (slot == 4 || slot == 5)
      return "(Team 2 General " + (slot - 3) + ")"
  }
  else if (type.value == "Archenemy") {
    if (slot == 1)
      return "(Archenemy)"
    else
      return "(Player " + slot + ")"
  }
}

function quickTag() {
  text = jQuery(this).html();
  newtext = jQuery("input#no_table_tags").val();
  if (newtext != "") 
    newtext = newtext + " " + text;
  else
    newtext = text;
  jQuery("input#no_table_tags").val(newtext);
}

function setPlayers(gametype, playerpos)
{
  var pform = jQuery("div#playerchoice")[0];
  players = enablePlayerselect(playerpos);
  var counter = 0;
  for (counter=0; counter<6; counter++) {
    pform.children[counter].id="p"+ (counter+1) + gametype + players +"p";
    if (counter < players)
      //enable visible players
      pform.children[counter].hidden=false;
    else {
      //If we're hiding, remove any players that were there
      if (pform.children[counter].children[0].children.length == 1) {
        movePlayer(jQuery("div#playerlist"), pform.children[counter].children[0].children[0].id);

      }
      pform.children[counter].hidden=true;
    }
    if (jQuery("div#playerslot" + (counter+1)).html().substring(0,5) == "Guest")
      jQuery("div#playerslot" + (counter+1)).html("Guest " + getSlotName(counter+1));
  }
  jQuery("div#playerchoice").removeClass();
  jQuery("div#playerchoice").addClass("c" + gametype + players + "p");
}


function gametype() {
  var type = jQuery("#no_table_gametype")[0].options[jQuery("#no_table_gametype")[0].selectedIndex];
  if (type.value == "Basic") {
    setPlayers(type.value, new Array(2, 3, 4, 5, 6));
  }
  else if (type.value == "2-headed") {
    setPlayers(type.value, new Array(4, 6));
  }
  else if (type.value == "Star") {
    setPlayers(type.value, new Array([5]));
  }
  else if (type.value == "Emperor") {
    setPlayers(type.value, new Array([6]));
  }
  else if (type.value == "Archenemy") {
    setPlayers(type.value, new Array(3, 4, 5, 6));
  }

}

function handleDragStart(e) {
  this.style.opacity = '0.7';  // this / e.target is the source node.

  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/html', this.id);
}

function handleDragEnd(e) {
  this.style.opacity = '1.0';  // this / e.target is the source node.
}

function handleDragOver(e) {
  if (e.preventDefault) {
    e.preventDefault(); // Necessary. Allows us to drop.
  }
  jQuery(this).addClass('dragactive');

  e.dataTransfer.dropEffect = 'move';  // See the section on the DataTransfer object.
  return false;
}


function handleDragEnter(e) {
  // this / e.target is the current hover target.
  jQuery(this).addClass('dragactive');
}

function handleDragLeave(e) {
  jQuery(this).addClass('draginactive');
  jQuery(this).removeClass('dragactive');
}

function handleDrop(e) {
  // this / e.target is current target element.

  if (e.stopPropagation) {
    e.stopPropagation(); // stops the browser from redirecting.
  }
  var newparent = jQuery(this);
  newparent.addClass('draginactive');
  newparent.removeClass('dragactive');

  var moveid = e.dataTransfer.getData('text/html');
  movePlayer(newparent, moveid);

  // See the section on the DataTransfer object.

  return false;
}

function handleTouchFrom(e) {
  e.stopPropagation();
  if (selected == this.id) {
    jQuery(this).removeClass("selected");
    selected = null;
    return;
  }

  if (selected != null) {
    selparent = jQuery("div#" + selected).parent();
    thisparent = jQuery(this).parent();
    // both are in the playerlist, chache which is selected
    if(selparent[0].id == "playerlist" && thisparent[0].id == "playerlist") {
      jQuery("div#" + selected).removeClass("selected");
      jQuery(this).addClass("selected");
      selected = this.id;
    }
    else {
      movePlayer(thisparent, selected);
      jQuery("div#" + selected).removeClass("selected");
      selected = null;
      //manage click event directly after move
      justmoved = true;
      setTimeout (clearMove, 100 );
    }
  }
  else {
    jQuery(this).addClass("selected");
    selected = this.id;
  }

}

function handleTouchTo(e) {
  e.stopPropagation();
  if (selected != null) {
    movePlayer(jQuery(this), selected);
    jQuery("div#" + selected).removeClass("selected");
    selected = null;
    //manage click event directly after move
    justmoved = true;
    setTimeout (clearMove, 100 );
  }
}

function clearMove(){
  justmoved = false;
}

jQuery(document).ready(function() {
  gametype();
  jQuery.event.props.push( "dataTransfer" );
  jQuery("select#no_table_gametype").change(gametype);
  jQuery("select#no_table_players").change(gametype);
  jQuery("div.dragfrom").bind('dragstart', handleDragStart);
  jQuery("div.dragfrom").bind('dragend', handleDragEnd);
  jQuery("div.dragto").bind('drop', handleDrop);
  jQuery("div.dragto").bind('dragover', handleDragOver);
  jQuery("div.dragto").bind('dragenter', handleDragEnter);
  jQuery("div.dragto").bind('dragleave', handleDragLeave);
  jQuery("div.quickadd").click(quickAdd);
  jQuery("span.quicktag").click(quickTag);
  jQuery("div.dragfrom").bind("touchend", handleTouchFrom);
  jQuery("div.dragto").bind("touchend", handleTouchTo);
  //prevent bubbling
  jQuery("div.quickadd").bind("touchend", function(e) {e.stopPropagation();});
  selected = null;
  justmoved = false;
});



