/* Convert a date to a local date of an anonymous visitor, browser dependant*/
document.addEventListener('DOMContentLoaded', function () {

  var dates = document.querySelectorAll("span.datetime");
  for( date of dates) {
    ms = date.dataset.seconds * 1000
    date.innerHTML = new Date(ms).toLocaleString();
  };
});
