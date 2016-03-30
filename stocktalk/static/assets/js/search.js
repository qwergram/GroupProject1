/**
 * Dictionary of US stocks for search suggestions 3/29/16.
 * http://api.jqueryui.com/autocomplete/#option-source
 */
$(function() {

    $( "#tags" ).autocomplete({
      source: "/static/raw_data/search.json"
    });

    $("#tags").keyup(function (e) {
        if (e.keyCode == 13) {
            window.location.href = "/detail/" + this.value
        }
    });
    console.log("search.js loaded");
});



