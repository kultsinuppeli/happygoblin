
jQuery(document).ready(function() {
  jQuery("select#playgroupselect").change(active_playgroup);
});

function active_playgroup(e) {
  var pg = jQuery("select#playgroupselect")[0].options[jQuery("select#playgroupselect")[0].selectedIndex].value;
  $.getJSON(app_prefix + 'default/active_playgroup.json?group=' + pg, function(data) {
    location.reload();
  });
}
