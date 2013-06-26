var _gaq = [['_setAccount', 'UA-26326068-1'], ['_trackPageview']];

(function() {
	var ga = document.createElement('script');
	ga.async = true;
	ga.src = 'http://www.google-analytics.com/ga.js';
	document.getElementsByTagName("BODY")[0].appendChild(ga);
})();

$(function() {
    $("select").change(function() {
        var left = $("select").first().val();
        var right = $("select").last().val();
        $(".select span").first().html(left);
        $(".select span").last().html(right);
        if(left == "None" && right == "None") {
            window.location = "about";
        } else if(left == "None") {
            window.location = right;
        } else if(right == "None") {
            window.location = left;
        } else {
            window.location = left + "..." + right;
        }
    });
});