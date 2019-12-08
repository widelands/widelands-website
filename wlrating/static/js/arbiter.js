function setButtons() {
    var addPlayerBtn = document.getElementById('add_player_btn');
    addPlayerBtn.addEventListener("click", function(event){
        event.preventDefault();
        addPlayer();
    }, false);
    var removePlayerBtn = document.getElementsByClassName('remove_player_btn');
    for (btn in removePlayerBtn) {
        html_btn = removePlayerBtn[btn]
        if (html_btn instanceof Element) {
            removePlayerBtn[btn].addEventListener("click", function(event){
                event.preventDefault();
                removePlayer(this);
            }, false);
        }
    }
    var isWinnerBtn = document.getElementsByClassName('is_winner_btn')
    for (btn in isWinnerBtn) {
        html_btn = isWinnerBtn[btn]
        if (html_btn instanceof Element) {
            isWinnerBtn[btn].addEventListener("click", function(event){
                event.preventDefault();
                isWinner(this);
            }, false);
        }
    }
}

function setAutocompletes() {
    $( ".player_username" ).autocomplete({
        source: '/rating/get_usernames/',
        minLength: 3,
    });
    $( ".player_map" ).autocomplete({
        source: '/rating/get_map/',
        minLength: 3,
    });
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
    // Set input value back to zero
    for (input in inputList) {
        if (inputList[input] instanceof Element) {
            inputList[input].value = '';
        }
    }
    tr.classList.toggle('to_hide');
}


function isWinner(html_btn) {
    var tr = html_btn.parentElement.parentElement;
    var team_number = tr.getElementsByClassName('player_team')[0].value;
    var result_input = document.getElementsByClassName('result')[0].value = team_number;
    
    var tbody = html_btn.parentElement.parentElement.parentElement.getElementsByTagName('tr');
    for (tr in tbody) {
        if (tbody[tr] instanceof Element) {
            var player_team_input = tbody[tr].getElementsByClassName('player_team')[0]
            if (player_team_input.value == team_number) {
                console.log(player_team_input.value);
                tbody[tr].classList.remove("looser");
                tbody[tr].classList.add("winner");
            }
            else {
                tbody[tr].classList.remove("winner");
                tbody[tr].classList.add("looser");
            }
        }
    }
    //console.log(team_number)
}