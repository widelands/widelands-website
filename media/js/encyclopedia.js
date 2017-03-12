$(document).ready(function() {
    var elem = document.getElementById('set_size');
    elem.addEventListener('click', set_size);
    checkb_names = ['sizes', 'types']; 
    // Initialize after reload, e.g. pressing F5
    init_checkboxes();
});

function set_size(){
    for (var y=0; y<checkb_names.length; y++){
        var option_boxes = document.getElementsByName(checkb_names[y]);
        for (var i = 0; i < option_boxes.length; i++) {
            elements = document.getElementsByName(option_boxes[i].value);
            for (var x = 0 ; x < elements.length; x++){
                if (option_boxes[i].checked){
                    elements[x].style.display = '';
                }else{
                    elements[x].style.display = 'none';    
                }
            }
        }
    }
    hide_tables();
}

function hide_tables(){
    var tables = document.getElementsByTagName('table');
    for (var i=0; i<tables.length; i++){
        var table = tables[i];
        var hidden_rows = 0;
        for (var x=0, row; row = table.rows[x]; x++){
            if (row.style.display == 'none'){
                hidden_rows++;
            }
        }
        if (table.rows.length == hidden_rows+1){
            table.style.display = 'none';
        }else{
            table.style.display = '';
        }
    }
}

function init_checkboxes(){
    for (var x=0; x<checkb_names.length; x++){
        var option_boxes = document.getElementsByName(checkb_names[x]);
        for (i=0; i < option_boxes.length; i++){
            option_boxes[i].checked = true;
        }
    }
}
