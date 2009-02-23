
function adjustLayout()  
{  
 // Get natural heights  
 var cHeight = xHeight("contentcontent");  
 var lHeight = xHeight("leftcontent");  
 var rHeight = xHeight("rightcontent");  
 
 // Find the maximum height  
 var maxHeight =  
   Math.max(cHeight, Math.max(lHeight, rHeight));  
 
 // Assign maximum height to all columns  
 xHeight("content", maxHeight);  
 xHeight("leftcolumn", maxHeight);  
 xHeight("rightcolumn", maxHeight);  
 xHeight("container", maxHeight);  
 
 // Show the footer  
 xShow("footer");  
}

window.onload = function()  
{  
 xAddEventListener(window, "resize",  
   adjustLayout, false);  
 adjustLayout();  
}  
