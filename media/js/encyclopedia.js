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
    if (sessionStorage.getItem('scripting_status') === "true"){
        $("#toggle_scripting")[0].checked = true;
        $(".scripting").show();
    }
    $("#toggle_scripting").click(function(){
        $(".scripting").toggle();
        sessionStorage.setItem('scripting_status', this.checked);
    });

    // Toggle the display of whole tables
    $("#small").click(function(){
        $(".size-S").toggle();
    });

    $("#medium").click(function(){
        $(".size-M").toggle();
    });

    $("#big").click(function(){
        $(".size-B").toggle();
    });

    $("#mines").click(function(){
        $(".size-I").toggle();
    });

    // Toggle rows of tables
    $("#warehouse").click(function(){
        $(".type-W").toggle( function(){
            hide_empty_tables();
        });
    });

    $("#production").click(function(){
        $(".type-P").toggle( function(){
            hide_empty_tables();
        });
    });

    $("#military").click(function(){
        $(".type-M").toggle( function(){
            hide_empty_tables();
        });
    });

    $("#training").click(function(){
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