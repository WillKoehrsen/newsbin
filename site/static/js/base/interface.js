// -----------------------------------------------------------------------------
// Functions

// build a url from a given base and arguments
function url( base, obj ){
	var result = [];
	for( var key in obj ){
		if( typeof(obj[key])!='function' ){
			result.push( key+'='+obj[key] );
		}
	}
	var result_str = base.prependif('/') + result.join('&').prependif('?');
	return result_str.replace(' ','%20');
}

// -----------------------------------------------------------------------------
// Network
var network = {
	// An interface for registering local endpoints
	// and then sending and receiving JSON data

	points:{},
	timeout:20000,

	get: function( endpoint, args ){
		if(endpoint in network.points){
			var handle = new XMLHttpRequest();
			var path = url( endpoint, args );

			handle.open("GET", path, true);

			handle.callback = network.points[endpoint];
			handle.onload = this.receive;
			handle.onerror = this.error;

			handle.timeout = this.timeout;
			handle.ontimeout = this.error;
			handle.send();
		}
	},

	post: function( endpoint, args ){
		if(endpoint in this.points){
			var handle = new XMLHttpRequest();
			var path = url( endpoint );
			var form = new FormData();

			for( var key in args ){
				form.append(key,args[key]);
			}

			handle.open("POST", path, true);

			handle.callback = network.points[endpoint];
			handle.onload = this.receive;
			handle.onerror = this.error;

			handle.timeout = this.timeout;
			handle.ontimeout = this.error;
			handle.send(form);
		}
	},

	register: function( endpoint, callback ){
		network.points[endpoint] = callback;
	},

	receive: function(){
		if(this.status==200){
			try{
				var response = JSON.parse(this.responseText);
				this.callback(response);
			} catch (error){
				console.log('ERROR:',error);
				console.log('RESPONSE:',this.responseText);
			}
		} else {
			this.callback({ summary:'Annotation Not Found' });
		}
	},

	error: function(){
		console.log(this);
	}

}

//network.register('articles', test);
//network.post('articles', { id:1 })
