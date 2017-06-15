// -----------------------------------------------------------------------------
// Article Window
var content = new Vue({
	el: '#js-capture-selection',
	data: {},
	methods: {
		capture: function( event ){
			var selection = window.getSelection();
			if( !selection.isCollapsed && selection.rangeCount==1 ){
				var range = selection.getRangeAt(0);
				if( range ){
					var input = document.getElementById('js-add-selection');
					input.value = range.toString();
				}
			}
		},
	}
});

var menu = new Vue({
	el: '#js-sidebar-menu',
	data:{
		active: false,
		input_tooltip: 'add or remove annotations',
	},
	methods: {
		open: function(){
			this.$data.active = true;
		},
		close: function(){
			this.$data.active = false;
		},
	}
});

var mobile = new Vue({
	el: '#js-mobile-menu',
	data:{
		article: true,
		menu: false,
	},
	methods: {
		toggle: function( event ){
			this.$data.article = this.$data.menu;
			if(this.$data.menu = !this.$data.menu){
				menu.open();
			} else {
				menu.close();
			}
		},
	},
});

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
// Modal Window
var annotation_defaults = {
	name:'',
	image:'',
	table:[],
	content:[],
	wikipedia_link:'',
	politifact_link:'',
};

var modal = new Vue({
	el: '#modal-annotation',
	data: annotation_defaults,
	methods: {
		close: function( event ){
			this.$el.style.display = "none";
			this.clear();
		},
		open: function( event ){
			this.$el.style.display = "flex";
		},
		clear: function( event ){
			Object.assign( this.$data, annotation_defaults);
		},
		fetch: function( name ){
			var handle = new XMLHttpRequest();
			var data = this.$data;
			var modal = this;

			handle.onload = function(){
				if(this.status==200){
					var response = JSON.parse(this.responseText);
					data.name = response.name;
					data.image = response.image;
					data.content = response.summary.split('\n\n');
					data.wikipedia_link = "https://en.wikipedia.org/wiki/"+response.name;
					for(var i = 0; i < response.data_table.length; i++){
						data.table.push( response.data_table[i] );
					}
					if(response.slug){
						data.politifact_link = "http://www.politifact.com/personalities/" + response.slug;
					}
					modal.open();
				}
			}

			handle.open("GET", '/annotations?name=' + name, true);
			handle.send();
		}
	}
});

// -----------------------------------------------------------------------------
// Plain JS
(function( annotations ){
	for( var i = 0; i < annotations.length; i++ ){
		var annotation = annotations[i];
		annotation.classList.add('highlight');
		annotation.addEventListener("click", function(_event){
			var name = this.getAttribute('name');
			modal.fetch( name );
		});
	}
})(document.getElementsByClassName('annotation'));

(function( block ){
    if(block){
        block.innerHTML = (new Date()).getFullYear();
    }
})(document.getElementById('js-year'));
