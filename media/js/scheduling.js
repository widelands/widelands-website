// global variables
var lastSelectedDates = []

// Create calandar and return it as an object. Useful for callbacks.
function createCalandar() {
    $('#scheduling-datepicker').multiDatesPicker({
        dateFormat: "yy-mm-dd",
        showAnim: "slideDown",
        numberOfMonths: 3,
        minDate: 0,
        onSelect: function(date) {
            selectedDate = date;
            updateAvailableDate(date)
        },
    });
}


//Add warning in case of disparency between browser and profil timezone
function addTimeZoneWarningIfNeeded() {
    var userTimeZone = document.getElementById('django-data').getAttribute('user-time-zone')
    var browserTimeZone = - new Date().getTimezoneOffset()/60
    if ( browserTimeZone != userTimeZone) {
        document.getElementById('timezone-error').removeAttribute("hidden");
        profilTime = document.getElementsByClassName('profil-time');
        for (var element in profilTime) {
            profilTime[element].innerHTML = cleanAndAddSign(userTimeZone);
        }
        document.getElementById('browser-time').innerHTML = cleanAndAddSign(browserTimeZone);
    }
}

function addPreviousDateFromUser(calendar) {
    //Populate the current date with already filled date by the user
    old_availabilities_string_JSON = document.getElementById('django-data').getAttribute('day-to-fill')
    old_availabilities_list = stringJSONtoJSList(old_availabilities_string_JSON)
    if (old_availabilities_list == "") {
        return;
    }
    dateToAdd = []
    for (var date in old_availabilities_list) {
        // Extract day of the date. See format in view.py.
        dateString = old_availabilities_list[date].substring(1,11);
        if (!existInList(dateToAdd, dateString)){
            dateToAdd.push(dateString)
            updateAvailableDate(dateString)
        }
    }
    $('#scheduling-datepicker').multiDatesPicker('addDates', dateToAdd);
    for (var date in old_availabilities_list) {
        // Extract hour of the date. See format in view.py.
        hourString = old_availabilities_list[date].substring(12,14);
        // Extract day of the date. See format in view.py.
        dateString = old_availabilities_list[date].substring(1,11);
        hourString = removeZeroIfUnderTen(hourString);
        displayHourForDate(dateString, hourString);
    }
}

function addOtherUsersAvailabilities() {
    //Populate the result area showing other users and their disponibilities
    if (document.getElementById('django-data').getAttribute('users-to-fill')) {
        var otherPlayerAvailabilitiesJSON = document.getElementById('django-data').getAttribute('users-to-fill');
        otherPlayerAvailabilities = JSON.parse(otherPlayerAvailabilitiesJSON)
    }
    noOtherUser = true;
    for (var user in otherPlayerAvailabilities) {
        noOtherUser = false;
        dateList = otherPlayerAvailabilities[user]
        for (var date in dateList) {
            createUserDivOrUpdateIt(user, dateList[date])
        }
    }
    if (noOtherUser) {
        document.getElementById('no-user-to-display').removeAttribute("hidden");
    }
}

function sendDataAsForm(calendar) {
    //Get informations from selected hours
    var selectedDates = $( "#scheduling-datepicker" ).multiDatesPicker( "getDates" );
    var selectedDatesList = [];
    for (var d in selectedDates) {
        //remove whitespace
        var dateID = 'day-' + selectedDates[d];
        dateObj = document.getElementById(dateID);
        if (dateObj) {
            hoursList = dateObj.getElementsByClassName('hours');
            selectedHours = dateObj.getElementsByClassName('selected');
            if (selectedHours[0]){
                for (var h in hoursList) {
                    if (hasClass(hoursList[h] , 'selected')){
                        var hourAsDate = selectedDates[d] + "T" + addZeroIfUnderTen(h);
                        selectedDatesList.push(hourAsDate);
                    }
                }
            } 
        }
    }
    //Send informations to server
    console.log(selectedDatesList);
    post('.', selectedDatesList)
}

//Add or remove available dates in the ui.
function updateAvailableDate(date) {
    newDateID = "day-" + date
    dateAlreadyExist = !!document.getElementById(newDateID);
    document.getElementById('second-step').removeAttribute('hidden');
    if (dateAlreadyExist) {
        document.getElementById(newDateID).remove();
    } else {
        var original = document.getElementById('day-template');
        // We clone the date and fix different attributes
        var newDate = original.cloneNode(true);
        newDate.id = "day-" + date;
        newDate.removeAttribute("hidden");
        var textDate = new Date(date);
        textDate = textDate.toDateString();
        newDate.getElementsByClassName('day-title')[0].innerHTML = '<h3>' + textDate + '</h3>';
        //We add the listeners to each hours One for the click event, the other for the hover when the mouse is pressed
        hoursObj = newDate.getElementsByClassName('hours');
        for (var i = 0; i < hoursObj.length; i++) {
            hoursObj[i].addEventListener('click', updateHour, false);
            hoursObj[i].addEventListener("mouseover", function(e){
                if(e.buttons == 1 || e.buttons == 3){
                    updateHour(e);
                }
            })
        }
        //we look for the order the new date should be in
        daysList = document.getElementById('days-wrapper').getElementsByClassName('days');
        //We finally add the new date
        document.getElementById('days-wrapper').appendChild(newDate);
    }

}

function updateHour (event) {
    var div = (event.fromElement ? event.fromElement : event.currentTarget);
    isAlreadySelected = hasClass(div, 'selected');
    if (isAlreadySelected) {
        div.className = 'hours';
    } else {
        div.className += ' selected';
    }
}

function displayHourForDate(date, hour, user) {
    var dateDivID = 'day-' + date
    if (user) {
        dateDivID = user + '-day-' + date
    }
    dateDiv = document.getElementById(dateDivID);
    hourDiv = dateDiv.getElementsByClassName('hours');
    for (var hourInDiv in hourDiv) {
        if (hourInDiv == hour) {
            hourDiv[hourInDiv].className += ' selected';
        }
    }
}

function createUserDivOrUpdateIt(user, availTime) {
    if (!document.getElementById("user-" + user)){
        var original = document.getElementById('other-user-template');
        // We clone the date and fix different attributes
        var otherUser = original.cloneNode(true);
        otherUser.id = "user-" + user;
        otherUser.removeAttribute("hidden");
        var jsEventHTML = "/messages/compose/" + user
        var imageHTML = '<img src="/wlmedia/forum/img/send_pm.png" alt="" class="middle"><span class="middle">Send PM</span>'
        var userTitle = otherUser.children[0]
        var button =  document.createElement("button");
        button.innerHTML = imageHTML;
        button.onclick = function(){
            window.location.href = '/messages/compose/' + user;
        }
        var usernameP = document.createElement('p')
        usernameP.innerHTML = user;
        userTitle.appendChild(usernameP)
        userTitle.appendChild(button)
    } else {
        otherUser = document.getElementById("user-" + user);
    }
    var dtavailTime = new Date(availTime + ":00:00");
    //Remove timezone offset which js automatically add...
    js_offset = dtavailTime.getTimezoneOffset()/60
    dtavailTime = dtavailTime.addHours(js_offset);
    textDate = dtavailTime.toDateString();
    var dateFormated = dtavailTime.getFullYear() + "-" + dtavailTime.getMonth() + '-' + dtavailTime.getDay()
    var availTimeFormated = dtavailTime.getHours()
    var originalDay = document.getElementById('other-day-template')
    if (!document.getElementById(user + "-day-" + dateFormated)) {
        var day = originalDay.cloneNode(true);
        day.id = user + "-day-" + dateFormated;
        day.removeAttribute("hidden");
        day.getElementsByClassName('day-title')[0].innerHTML = '<h3>' + textDate + '</h3>'; 
        otherUser.appendChild(day);
    }
    document.getElementById('other-users-wrapper').appendChild(otherUser);
    displayHourForDate(dateFormated, availTimeFormated, user);
}

/*****************************/
/********* utilities *********/
/*****************************/
// read as "Stackoverflow coded this"
function hasClass(element, cls) {
    return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
}

//We need a custom function to submit a form because our data isn't formated as a form.
function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.
    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);
    for(var key in params) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
    }
    //CSRF token
    var csrf_div = document.createElement("div");
    csrf_div.innerHTML = document.getElementById('django-data').getAttribute('csrf-token')
    form.appendChild(csrf_div);
    document.body.appendChild(form);
    form.submit();
}

function cleanJSONfromWhiteSpace(json) {
    var name, newName;
    for (var name in json) {
        // Get the name without spaces
        newName = name.replace(/ /g, "");
        // If that's different...
        if (newName != name) {
            // Create the new property
            json[newName] = json[name];
            // Delete the old one
            delete json[name];
        }
    }
    return json;
}

function stringJSONtoJSList(json) {
    //removes brackets
    json = json.substring(1, json.length-1);
    var jsonList= json.split(",")
    for (var i in jsonList){
        jsonList[i] = jsonList[i].replace(/\s/g, '');
    }
    return jsonList

}

function addZeroIfUnderTen(number) {
    return ('0' + number).slice(-2)
}

function removeZeroIfUnderTen(number) {
    return parseInt(number, 10);
}

Date.prototype.addHours = function(h) {    
   this.setTime(this.getTime() + (h*60*60*1000)); 
   return this;   
}

function existInList(list, value) {
    return list.indexOf(value) > -1
}

function cleanAndAddSign(number) {
    if (number < 0) {
        return ' ' + parseInt(number)
    } else {
        return '+ ' + parseInt(number)
    }
}