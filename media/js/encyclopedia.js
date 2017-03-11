$(document).ready(function() {
    var elem = document.getElementById('set_size');
    elem.addEventListener('click', set_size);
    elem = document.getElementById('set_type');
    elem.addEventListener('click', set_type);
    // Initialize after reload, e.g. pressing F5
    init_checkboxes('sizes');
    //init_checkboxes('types');
});

function set_size(){
    var option_boxes = document.getElementsByName("sizes");
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

function init_checkboxes(n){
    var option_boxes = document.getElementsByName(n);
    for (i=0; i < option_boxes.length; i++){
        option_boxes[i].checked = true;
    }
}