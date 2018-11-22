$(document).ready(function() {

    // Smooth scrolling, taken from:
    // http://stackoverflow.com/a/18795112
    $("a[href*='#']").click(function(event){
        $('html, body').animate({
            scrollTop: $( $.attr(this, 'href') ).offset().top
        }, 500);
        event.preventDefault();
    });

    // Toggle display of scripting values
    // Usage of sessionStore makes it possible to keep the status
    // when switching to different pages. When switching the page the
    // state of checkbox and the visibility of items has to be set.
    if ( $("input#toggle_scripting").length > 0 &&
        sessionStorage.getItem('scripting_status') === "true"){
        $("input#toggle_scripting")[0].checked = true;
        $(".scripting").show();
    }
    $("input#toggle_scripting").click(function(){
        $(".scripting").toggle();
        sessionStorage.setItem('scripting_status', this.checked);
    });

    // Toggle the display of whole tables
    $("input#small").click(function(){
        $(".size-S").toggle();
    });

    $("input#medium").click(function(){
        $(".size-M").toggle();
    });

    $("input#big").click(function(){
        $(".size-B").toggle();
    });

    $("input#mines").click(function(){
        $(".size-I").toggle();
    });

    // Toggle rows of tables
    $("input#warehouse").click(function(){
        $(".type-W").toggle( function(){
            hide_empty_tables();
        });
    });

    $("input#production").click(function(){
        $(".type-P").toggle( function(){
            hide_empty_tables();
        });
    });

    $("input#military").click(function(){
        $(".type-M").toggle( function(){
            hide_empty_tables();
        });
    });

    $("input#training").click(function(){
        $(".type-T").toggle( function(){
            hide_empty_tables();
        });
    });

});

function hide_empty_tables(){
    // Hide a whole table if no row is displayed in it
    var tables = $("table");
    for (var i=0; i<tables.length; i++){
        var table = tables[i];
        var hidden_rows = 0;
        for (var x=0, row; row = table.rows[x]; x++){
            if (row.style.display == 'none'){
                hidden_rows++;
            }
        }
        // +1 here because we need to count also <th>
        if (table.rows.length == hidden_rows+1){
            table.style.display = 'none';
        }else{
            table.style.display = '';
        }
    }
}