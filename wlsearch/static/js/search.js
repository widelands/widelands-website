/* Functions used for the search */

/* Show a jquery datepicker when clicking on an element with this class */
$( function() {
    $( ".datepicker" ).datepicker({
        dateFormat: "yy-mm-dd",
        showAnim: "slideDown",
        defaultDate: '-1y'
        });
  });

/* Hide elements which has this class */
/* TODO (Franku): Consider to use this also in wiki */
$( function() {
    $( ".closeable" ).click(function() {
      if ( $( this.nextElementSibling ).is( ":hidden" ) ) {
        $( this.nextElementSibling ).show( "slow");
      } else {
        $( this.nextElementSibling ).slideUp( "slow");
        }
    });
});
