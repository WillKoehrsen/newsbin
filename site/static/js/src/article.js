

// -----------------------------------------------------------------------------
// Annotation:
//		a modal component that displays when an x-annotation is clicked
var modal = (function( target ){
	target.refs = {};
	var children = target.getElementsByTagName('div');
	for( var i=0; i<children.length; i++ ){
		var ref = children[i].getAttribute('ref');
		if(ref){ target.refs[ref] = children[i]; }
	}

	handlers = {
		close:function(){
			for(ref in target.refs){ target.refs[ref].innerHTML = ''; }
			target.style.display = 'none';
		},
		open:function( name ){
			var handle = new XMLHttpRequest();
			var refs = target.refs;

			handle.onload = function(){
				if(this.status==200){
					var response = JSON.parse(this.responseText);
					refs.close.innerHTML = 'Close';
					refs.title.innerHTML = response.name;
					refs.image.innerHTML = '<img src="'+response.image+'"/>';

					var content = response.summary.split('\n\n')
					content.forEach(function( p ){
						refs.content.innerHTML += '<p>'+p+'</p>';
					});

					refs.links.innerHTML += '<a href="https://en.wikipedia.org/wiki/'+response.name+'" target="_blank">on wikipedia</a>';
					if(response.slug){ refs.links.innerHTML += '<a href="http://www.politifact.com/personalities/'+response.slug+'" target="_blank">on politifact</a>'; }

					response.data_table.forEach(function( item ){
						refs.data.innerHTML += '<div class="modal-data-item">\
													<div>'+item.key+'</div>\
													<div>'+item.value+'</div>\
												</div>';
					});
					
					target.style.display = 'flex';
				} else {
					console.log(this.status);
				}
			}

			handle.open("GET", '/annotations?name=' + name, true);
			handle.send();
		},
	}

	return handlers;
})( document.getElementById('js-modal-annotation') );

var annotations = document.getElementsByClassName('annotation');
if(annotations){
	for( var i = 0; i < annotations.length; i++ ){
		annotations[i].addEventListener("click", function(_event){
			modal.open(this.getAttribute('name'));
		});
	}
}

var content = document.getElementById('js-capture-selection');
if(content){
	content.addEventListener('mouseup',function(){
		var selection = window.getSelection();
		if( !selection.isCollapsed && selection.rangeCount==1 ){
			var range = selection.getRangeAt(0);
			var input = document.getElementById('js-add-selection');
			if( input && range ){
				input.value = range.toString();
			}
		}
	});
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
