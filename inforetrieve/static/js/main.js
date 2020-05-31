$(document).ready(function() {
  $(".search").keyup(function(){
  $.get("/reviews/search", {"text": $(this).val()}, function(data, status){
    $("#search_text").html(data)
  });
});
});

