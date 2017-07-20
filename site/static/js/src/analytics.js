function set_tracking_info( value ){
	try { localStorage['newsbin_visited'] 	= value; return true; } catch(e){}
	try { sessionStorage['newsbin_visited'] = value; return true; } catch(e){}
	return false;
}

function send( analytics ){
	console.log(analytics);
}

(function(){
	// this function gathers information about visitors
	// and submits it when they leave the current page

	// -------------------------------------------------------------------------
	// Flags/Meta
	var new_visitor 	= true;
	var last_visited	= new Date().toUTCString();

	// -------------------------------------------------------------------------
	// Datetimes
	var time_arrived	= new Date();
	var time_offset		= time_arrived.getTimezoneOffset();
	var time_left		= null;
	var time_on_page	= null;

	// -------------------------------------------------------------------------
	// System/Browser Information
	var referrer			= document.referrer;
	var language			= navigator.userLanguage || navigator.language;
	var platform			= navigator.platform;
	var user_agent			= navigator.userAgent;

	var window_width		= window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
	var window_height		= window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
	var color_depth			= screen.colorDepth;

	// -------------------------------------------------------------------------
	// Touch Support
	var touch_support		=	'ontouchstart' in window ||
								window.DocumentTouch && document instanceof window.DocumentTouch ||
								navigator.maxTouchPoints > 0 || window.navigator.msMaxTouchPoints > 0;

	// -------------------------------------------------------------------------
	// Storage
	var session_store		= (sessionStorage != undefined);
	var local_store			= (localStorage != undefined);
	var storage_disabled	= !(session_store || local_store);

	// try to get tracking info if it exists
	if('newsbin_visited' in localStorage || 'newsbin_visited' in sessionStorage){
		new_visitor			= false;
		last_visited		= localStorage['newsbin_visited'] || sessionStorage['newsbin_visited'];
	}

	// try to set updated tracking information or storage is disabled
	if(set_tracking_info( time_arrived.toUTCString() ) ){
		storage_disabled	= false;
	}

	// -------------------------------------------------------------------------
	// Plugins
	var plugins				= [];

	for( var i=0; i<navigator.plugins.length; i++ ){
		var plugin = navigator.plugins[i];

		// get a simplified object for each
		// plugin.
		plugins.push({
			description:plugin.description,
			filename:plugin.filename,
			name:plugin.name,
		})

	}

	// -------------------------------------------------------------------------
	// On Leave
	window.addEventListener('beforeunload',function(){
		time_left = new Date();
		time_on_page = (time_left - time_arrived);

		send({
			'new_visitor':new_visitor,
			'time_arrived':time_arrived,
			'time_offset':time_offset,
			'time_left':time_left,
			'time_on_page':time_on_page,
			'last_visited':last_visited,
			'referrer':referrer,
			'language':language,
			'platform':platform,
			'user_agent':user_agent,
			'touch_support':touch_support,
			'session_store':session_store,
			'local_store':local_store,
			'storage_disabled':storage_disabled,
			'plugins':plugins,
			'window':{
				'width':window_width,
				'height':window_height,
				'color_depth':color_depth,
			},
		});
	});

})();
