
$( function() {
    $( "#toggleMenu" ).on( "click", function() {
          $( ".responsiveHidden" ).toggle( "slow" );
    });
});

$( function() {
    $( "#loginButton" ).on( "click", function() {
          $( "#responsiveLogin" ).toggle( "slow" );
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
