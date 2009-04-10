/*
 * jQuery Disable On Submit Plugin
 * http://www.evanbot.com/article/jquery-disable-on-submit-plugin/13
 *
 * Copyright (c) 2009 Evan Byrne (http://www.evanbot.com)     
 */
$.fn.disableOnSubmit = function(disableList){
	
	if(disableList == null){var $list = 'input[type=submit],input[type=button],input[type=reset],button';}
	else{var $list = disableList;}
	
	// Makes sure button is enabled at start
	$(this).find($list).removeAttr('disabled');
	
	$(this).submit(function(){$(this).find($list).attr('disabled','disabled');});
	return this;
};