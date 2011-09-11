{% comment %}
    vim:ft=htmldjango:
{% endcomment %}
{% load threadedcommentstags %}

<script type="text/javascript">
<!--
function show_reply_form(comment_id, url, person_name) {
    var comment_reply = $('#' + comment_id);
    var to_add = $( new Array(
    '<div class="response"><p>Reply to ' + person_name + ':</p>',
    '<form method="POST" action="' + url + '?next={{object.get_absolute_url}}">',
    '<div class="comment_post">',  '<div class="comment text"> <span class=errorclass">{{ form.comment.errors }}</span>{{ form.comment }}',  
    '</div> <input type="hidden" name="markup" value="1" />',
        '<input type="submit" value="Submit Comment" />',
        '</div>', "{% csrf_token %}", '</form>', '</div>').join(''));
    to_add.css("display", "none");
    comment_reply.after(to_add);
    to_add.slideDown(function() {
        comment_reply.replaceWith(new Array('<a id="',
        comment_id,'" href="javascript:hide_reply_form(\'',
        comment_id, '\',\'', url, '\',\'', person_name,
        '\')">Stop Replying</a>').join(''));
    });

    check_posting();
}
function hide_reply_form(comment_id, url, person_name) {
    var comment_reply = $('#' + comment_id);
    comment_reply.next().slideUp(function (){
        comment_reply.next('.response').remove();
        comment_reply.replaceWith(new Array('<a id="',
        comment_id,'" href="javascript:show_reply_form(\'',
        comment_id, '\',\'', url, '\',\'', person_name,
        '\')">Reply</a>').join(''));
    });
    
   check_posting();
}
-->
</script>


