// -----------------------------------------------------------------------------
// Localize the datetime on under the title
var block = document.getElementById('js-localize-date');
if(block!=null){
	var date = new Date( block.getAttribute('iso') );
	block.innerHTML = date.toLocaleDateString() + " " + date.toLocaleTimeString();
}

// -----------------------------------------------------------------------------
// VueJS
var annotation_defaults = {
	name:'',
	image:'',
	table:{},
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
		},
		open: function( event ){
			this.$el.style.display = "flex";
		},
		clear: function( event ){
			Object.assign( this.$data, annotation_defaults);
		},
	}
});

var add = new Vue({
	el: '#js-add-selection',
	data: { value:''}
});

var annotation {
	template: '<x-annotation>{{ name }}</x-annotation>',
	data: function () {
		return {};
	}
}

var content = new Vue({
	el: '#js-capture-selection',
	components: {
		'annotation':annotation,
	},
	methods: {
		capture: function( event ){
			var selection = window.getSelection();
			if( !selection.isCollapsed && selection.rangeCount==1 ){
				var range = selection.getRangeAt(0);
				if( range ){
					add.$data.value = range.toString();
				}
			}
		},
	}
});

/* -------------------------------------------------------------------------- */
/* Plain JS */
var annotations = document.getElementsByClassName('annotation');
if(annotations){
	for( var i = 0; i < annotations.length; i++ ){
		annotations[i].addEventListener("click", function(_event){
			var name = this.getAttribute('name');
			var handle = new XMLHttpRequest();
			var url = '/annotations?name=' + name;

			handle.onload = function(){
				if(this.status==200){
					var response = JSON.parse(this.responseText);
					modal.clear();

					modal.$data.name = response.name;
					modal.$data.image = response.image;
					modal.$data.content = response.summary.split('\n\n');
					if(response.truth_score){
						modal.$data.table['truth_score'] = {
								key:"Truth Score",
								value:response.truth_score+"%",
								tooltip:'calculated from the last five statements fact-checked by politifact.com'
							};
					}
					if(response.slug){
						modal.$data.politifact_link = "http://www.politifact.com/personalities/" + response.slug;
					}
					modal.$data.wikipedia_link = "https://en.wikipedia.org/wiki/" + response.name;

					modal.open();
				}
			}

			handle.open("GET", url, true);
			handle.send();
		});
	}
}

menu_tab = document.getElementById('js-tab-menu');
article_tab = document.getElementById('js-tab-article');
menu_form = document.getElementById('js-sidebar-anno-menu');

if(menu_tab){
    menu_tab.addEventListener('click',function(_event){
        if(this.classList.toggle('current')){
            article_tab.classList.remove('current');
            menu_form.classList.add('open');
        } else {
            article_tab.classList.add('current');
            menu_form.classList.remove('open');
        }
    });
}

if(article_tab){
    article_tab.addEventListener('click',function(_event){
        if(this.classList.toggle('current')){
            menu_tab.classList.remove('current');
            menu_form.classList.remove('open');
        } else {
            menu_tab.classList.add('current');
            menu_form.classList.add('open');
        }
    });
}
