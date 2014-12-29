$( document ).ready(function() {
  $(document).foundation();

  //organisation name
  $('#start_details #name').keypress(
    function(){
        //fake a name check
        if($('#start_details #name').val().length >= 4){
            $('form ul.verified-facts').show();
        } else {
            $('form ul.verified-facts').hide();
        }
    }
  );

  //directors
  $("#director_count").change(function() {
    if ($("#director_count").val() && $("#director_count").val() > 0){
      $('#director_contact').show();
    }else{
      $('#director_contact').hide();
    }
  });

  //done
  if ($("#done-pending").length > 0 && $("#done-done").length > 0){
    $("#done-done").hide();
    setTimeout(function() {
      $("#done-done").show();
      $("#done-pending").hide();
      if (navigator.vibrate !== undefined) {
        navigator.vibrate(1000);
      }
    }, 5000);
  }
});
