
function setAddPlayerBtn() {
    var addPlayerBtn = document.getElementById('add_player_btn');
    addPlayerBtn.addEventListener("click", function(event){
        event.preventDefault()
        addPlayer()
    }, false);
    var removePlayerBtn = document.getElementsByClassName('remove_player_btn')
    for (btn in removePlayerBtn) {
        html_btn = removePlayerBtn[btn]
        if (html_btn instanceof Element) {
            removePlayerBtn[btn].addEventListener("click", function(event){
                event.preventDefault()
                removePlayer(this)
            }, false);
        }
    }
    
}

function addPlayer() {
    var table = document.getElementById('add_player_table');
    var hidden_elements = table.getElementsByClassName('to_hide');
    if (hidden_elements[0]) {
        hidden_elements[0].classList.toggle('to_hide');
    }
}

function removePlayer(html_btn) {
    var tr = html_btn.parentElement.parentElement
    var inputList = tr.getElementsByTagName('input')
    for (input in inputList) {
        if (inputList[input] instanceof Element) {
            inputList[input].value = '';
        }
    }
    tr.classList.toggle('to_hide');
    console.log(inputList)
}
