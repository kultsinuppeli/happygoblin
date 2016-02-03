function good_name(isgood, buttonid) {
  if (isgood) {
    jQuery("button#" + buttonid).removeClass('badbutton');
    jQuery("button#" + buttonid).addClass('goodbutton');
  }
  else {
    jQuery("button#" + buttonid).removeClass('goodbutton');
    jQuery("button#" + buttonid).addClass('badbutton');
  }

}

function check_name(checkfunc, inputid, buttonid) {
  var name = jQuery("input#" + inputid).val();

  if (name.length <=3 || name.length > 50 ){
    good_name(false, buttonid);
  }
  else {
    $.getJSON(app_prefix + checkfunc + '.json?name='+name, function(data) {
      if (data['free']) 
        good_name(true, buttonid);
      else
        good_name(false, buttonid);
    });
  }
}

function register(createfunc, confirmid, data, redirect) {
  if (jQuery("button#" + confirmid).hasClass("goodbutton")) {

    $.ajax({  
       url: app_prefix + createfunc + '.json',
       type:'POST',  
       dataType: 'Json',

       data: JSON.stringify(data),
       
      success: function(data) {  
        if (redirect) {
          window.location = redirect;
        }
      }    
    });   
  } 
}

  

