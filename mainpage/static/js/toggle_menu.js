
$( function() {
    $( "#toggleMenu" ).on( "click", function() {
          $( ".respMenuHidden" ).toggle( "slow" );
    });
});

$( function() {
    $( "#respLoginButton" ).on( "click", function() {
          $( "#responsiveLogin" ).toggle( "slow" );
    });
});

$( function() {
    $( "#respAsideButton" ).on( "click", function() {
          $( ".columnModule" ).toggle( "slow" );
    });
});
/*
function toggleHidden(cl) {
  var x = document.getElementsByClassName(cl);
  */
/*if (x.className === "topnav") {
    x.className += " responsive";
  } else {
    x.className = "topnav";
  }*//*

}
*/
