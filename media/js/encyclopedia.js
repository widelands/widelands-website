$(document).ready(function() {
    var elem = document.getElementById('apply_filter');
    elem.addEventListener('click', set_display);
    // Find names of checkboxes:
    checkb_names = get_input_names(); 
    // Initialize after reload, e.g. pressing F5:
    init_checkboxes();

    // Smooth scrolling, taken from:
    // http://stackoverflow.com/a/18795112
    $('a[href*=#]').click(function(event){
        $('html, body').animate({
            scrollTop: $( $.attr(this, 'href') ).offset().top
        }, 500);
        event.preventDefault();
    });
});

function get_input_names(){
    var inp = document.getElementById('filter_select').getElementsByTagName('input');
    var n = [];
    for (var i=0; i<inp.length; i++){
        if (! n.includes(inp[i].name)){
            n.push(inp[i].name);
            }
    }
    return n;
}

function set_display(){
    // Hide/unhide tables and/or rows
    // Tables get hidden when filtering by size
    // Rows get hidden when filtering by type
    for (var y=0; y<checkb_names.length; y++){
        var option_boxes = document.getElementsByName(checkb_names[y]);
        if ( check_checked(option_boxes) === false ){
            // Mark all as checked if none is checked for one type of filter
            // This makes it possible to search e.g. for all of type
            // 'Production' (and no 'size' is checked), or all of size
            // 'Big' (and no 'type' is checked)
            for (var j=0; j<option_boxes.length; j++){
                option_boxes[j].checked = true;
            }
        }
        for (var i = 0; i < option_boxes.length; i++) {
            var elements = document.getElementsByName(option_boxes[i].value);
            hide_unhide_elements(elements, option_boxes[i].checked);
        }
    }
    // Filtering by type may lead into empty tables resulting in showing just
    // rows with <th> or caption
    hide_empty_tables();
}

function hide_unhide_elements(elem_list, checked){
    elem_list.forEach( function(elem){
        if (checked){
            elem.style.display = '';
        }else{
            elem.style.display = 'none';
        }
    });
}

function check_checked(chb_list){
    // Check if none of the checkbox is checked in this list
    var c=0;
    chb_list.forEach( function(chb){
        if (! chb.checked){
            c++;
        }
    });
    if (c == chb_list.length){
        return false;
    }
    return true;
}

function hide_empty_tables(){
    // Hide a table if no row is displayed in it
    var tables = document.getElementsByTagName('table');
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

function init_checkboxes(){
    // Mark all checkboxes as checked
    for (var x=0; x<checkb_names.length; x++){
        var option_boxes = document.getElementsByName(checkb_names[x]);
        for (i=0; i < option_boxes.length; i++){
            option_boxes[i].checked = true;
        }
    }
}
