jQuery.fn.sexyVote = function(config) {
    config = config || {};
    var defaults = {
        activeImageSrc: "active_star.gif",
	passiveImageSrc: "passive_star.gif",
	maxScore: 5,
	fn: new Function(),
	messages: [
	    "Your vote have been saved.",
	    "Very bad",
	    "Bad",
	    "Good, but could be better",
	    "Good enough",
	    "Very good"
	]
    };   
    
    config = jQuery.extend(defaults, config);
    
  
    
    return this.each(function() {
        var $container = jQuery(this);
	
	for (var i = 0, num = config.maxScore * 2; i < num; ++i) {
	    jQuery("<img />").appendTo($container);    
	}
	
	jQuery("<span />").appendTo($container);
	
	$container.find("img:even").
	attr("src", config.passiveImageSrc).
	css({display: "inline"}).
	on("mouseover", function(e) {	    
	    var len = $container.find("img:even").index(e.target) + 1;
	    
	    $container.find("img:even").slice(0, len).css({display: "none"});
	    
	    $container.find("img:odd").slice(0, len).css({display: "inline"});
	    
	    $container.find("span").text(config.messages[len]);
	    
	    
	}).
	end().
	find("img:odd").
	attr("src", config.activeImageSrc).
	css({display: "none"}).
	on("mouseout", function(e) {

	    var len = $container.find("img:odd").
	    index(e.target) + 1;

	    $container.find("img:odd")
	    .slice(0, len).
	    css({display: "none"});
	    $container.find("img:even").
	    slice(0,  len).
	    css({display: "inline"});
	    
	    $container.find("span").
	    text("");
	    
	        
	}).
	on("click", function(e) {
	    $container.find("img").
	    off("mouseover").
	    off("mouseout").
	    off("click");
	    $container.find("span").
	    text(config.messages[0]);
	    config.fn.call(this, e, $container.find("img:odd").index(e.target) + 1);
	});
    });
}; 
