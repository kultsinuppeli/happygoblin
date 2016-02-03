
jQuery(document).ready(function() {
  $.getJSON('list_ongoing_games.json', function(data) {
    print_ongoing_games(data["games"], jQuery("div#ongoing_games"))
  });
  $.getJSON('list_games.json?amount=10', function(data) {
    print_games(data["games"], jQuery("div#latest_games"))
  });
});