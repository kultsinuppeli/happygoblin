

function toggle_admin() {
  var playgroup = this.id.split("-")[1];
  var player = this.id.split("-")[2];
  var admin = false;
  if (this.checked) 
    admin = true;

  $.ajax({  
      url: app_prefix + 'settings/set_admin.json',
      type:'POST',  
      dataType: 'Json',
      data: JSON.stringify({playerid: player, admin: admin, playgroup: playgroup}),
      success: function(data) {  
        
      }    
    });   
}

function merge_deck() {
  var mergefrom = this.id.split("-")[1];
  var mergeto = jQuery("#select-" + mergefrom)[0].options[jQuery("#select-" + mergefrom )[0].selectedIndex].value;
  var data = JSON.stringify({sourceid: mergefrom, targetid: mergeto });
  merge("settings/merge_decks", data);
}

function merge_player() {
  if (! jQuery(this).hasClass("badbutton")) {
    var playgroup = this.id.split("-")[1];
    var mergefrom = this.id.split("-")[2];
    var mergeto = jQuery("#select-" + playgroup + "-" + mergefrom)[0].options[jQuery("#select-" + playgroup + "-" + mergefrom)[0].selectedIndex].value;
    var data = JSON.stringify({sourceid: mergefrom, targetid: mergeto, playgroup: playgroup})
    merge("settings/merge_players", data);
  } 
}

function merge(merge_func, data) {
  bootbox.confirm("Are you sure? This can not be undone!", function(result) {
    if (result == true) {
      $.ajax({  
        url: app_prefix + merge_func + '.json',
        type:'POST',  
        dataType: 'Json',
        data: data,

        success: function(data) {
          window.location.reload(true);
        }    
      });
    }
  });
}

function invite_player() {
  var playgroup = this.id.split("-")[1];
  var data = {playername: jQuery("input#inviteinput-" + playgroup).val(), playgroup: playgroup};
  register("settings/invite_player", "invitebutton-" + playgroup, data, "playgroup");
}

function uninvite_player() {
  var playgroup = this.id.split("-")[1];
  var player = this.id.split("-")[2];

  $.ajax({  
       url: app_prefix + 'settings/cancel_invitation.json',
       type:'POST',  
       dataType: 'Json',

       data: JSON.stringify({playerid: player, playgroup: playgroup}),
       
      success: function(data) {  
        window.location.reload(true);
      }    
    });   
}

function join_group() {
  var playgroup = this.id.split("-")[1];
  $.ajax({  
       url: app_prefix + 'settings/join_group.json',
       type:'POST',  
       dataType: 'Json',
       data: JSON.stringify({"playgroup": playgroup}),
       
      success: function(data) {  
        window.location.reload(true);       
      }    
    });   
}

function check_user() {
  var playgroup = this.id.split("-")[1];
  check_name("register/check_username", this.id, "confirm-user-" + playgroup);
}

function check_invite(event, item) {
  if (!item) {
    var item = this;
  }
  var id = item.id.split("-")[1];
  var val = jQuery("input#inviteinput-" + id).val();
  if (jQuery.inArray(val, invitelist[id]) > -1 ) {
    good_name(true, "invitebutton-" + id );
  } else {
    good_name(false, "invitebutton-" + id );
  }

}

function add_user() { 
  var playgroup = this.id.split("-")[2];
  var data = {playername: jQuery("input#username-" + playgroup).val(), playgroup: playgroup};
  register("settings/add_player", "confirm-user-" + playgroup, data, "playgroup");  
}

function add_group() {
  var data = {groupname: jQuery("input#groupname").val()};
  register("settings/create_group", "confirm-group", data, "playgroup");
}

function active_tab() {
  var oldid = jQuery("div.activetab").attr("id").split("-")[1];
  var newid =  this.id.split("-")[1];
  jQuery("div.activetab").removeClass("activetab");
  jQuery(this).addClass("activetab");
  jQuery("div#playgroup-" + oldid).hide();
  jQuery("div#playgroup-" + newid).show();
}

function disable_merge_for_playing() {
  $.ajax({  
      url: app_prefix + 'settings/is_player_playing.json',
      type:'POST',  
      dataType: 'Json',
      data: JSON.stringify({"player": this.id.split("-")[2],
                            "playgroup": this.id.split("-")[1]}),
      success: function(data) {  
          if (data["playing"]) {
            jQuery("button#merge-" + data["playgroup"] + "-" + data["player"]).addClass("badbutton");
          }
      }
    });
}