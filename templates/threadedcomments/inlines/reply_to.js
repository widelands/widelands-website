{% comment %}
    vim:ft=htmldjango:
{% endcomment %}
{% load threadedcomments_tags %}
{% load wlprofile %}

<script type="text/javascript">
function show_reply_form(comment_id, url, depth) {
	var comment = $('#' + comment_id);
	var reply_link = $('#' + comment_id + " .reply_link");
	var reply_form = $('<div class="comment odd response" style="margin-left: ' + (depth+1) +'cm;">'
			+ '<table>'
				+ '<tr>'
					+ '<td class="author">'
                {% if post.user.wlprofile.avatar %}
						+ '<a href="{% url profile_view user %}">'
							+ '<img style="width: 50px; height: 50px;" src="{{ user.wlprofile.avatar.url }}" />'
						+ '</a>'
                {% endif %}
						+ '<br />'
						+ '<span class="small">{{ user|user_link }}</span>'
					+ '</td>'
					+ '<td class="text">'
						+ '<form method="POST" action="' + url + '?next={{object.get_absolute_url}}">'
							+ '<span class="errormessage">{{ form.comment.errors }}</span>'
							+ '{{ form.comment }}'
							+ '<br />'
							+ '<input type="hidden" name="markup" value="1" />'
							+ '<input type="submit" value="Submit Comment" />'
							+ '<button type="button" onclick="javascript:hide_reply_form(\''+comment_id+'\', \''+url+'\', '+depth+')">Cancel</button>'
							+ "{% csrf_token %}"
							+ '</form>'
					+ '</td>'
				+ '</tr>'
			+ '</table>'
		+ '</div>');
	reply_form.css("display", "none");
	comment.after(reply_form);
	reply_link.html('<a href="javascript:hide_reply_form(\''+comment_id+'\', \''+url+'\', '+depth+')">Stop Replying</a>');
	reply_form.slideDown(function() {});
}

function hide_reply_form(comment_id, url, depth) {
	var comment = $('#' + comment_id);
	var reply_link = $('#' + comment_id + " .reply_link");
	reply_link.html('<a href="javascript:show_reply_form(\''+comment_id+'\', \''+url+'\', '+depth+')">Reply</a>');
	comment.next('.response').slideUp(function() {
		comment.next('.response').remove();
	});
}
</script>


