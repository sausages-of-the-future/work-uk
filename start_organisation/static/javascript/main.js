$( document ).ready(function() {
  $(document).foundation();

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

});
