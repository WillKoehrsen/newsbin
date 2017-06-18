// -----------------------------------------------------------------------------
// implement forEach if we're in IE
if (!NodeList.prototype.forEach) {
    NodeList.prototype.forEach = function(fn, scope) {
        for(var i = 0, len = this.length; i < len; ++i) {
            fn.call(scope, this[i], i, this);
        }
    }
}

/* -----------------------------------------------------------------------------
	OPTIONS
		This immediately invoked function operates over options in the left side
		menu of the index and about pages and does the following:

		1.	Shortcuts the input contained by the option (label) to the option.box
			attribute.

		2.	Adds an onchange event listener to the 'all' button as well as the
			rest of the options that calls either 'all_label' (for all) or 'default'
			(for the rest) on a change in value.

		3.	'all_label' sets all other checkboxes to its own value.

		4.	'default' checks that all options (aside from all) are checked, and
			sets all or unsets all based on that.
*/
var options = (function( buttons ){
	var all = null;
	var opts = [];

	// for each option button (left menu) . . .
	for(var i = 0; i < buttons.length; i++){

		// sort them into 'all' or 'opts'
		var item = buttons[i];
		if(item.id=='all_label'){ all=item; }
		else { opts.push(item); }

		// shortcut the inner input (the checkbox) to an
		// attribute for conveniance
		item.box = item.getElementsByTagName('input')[0];

        // if we have a value stored in sessionStorage,
        // we need to load it.
        if(item.box.id in sessionStorage){
            item.box.checked = sessionStorage.getItem(item.box.id)!='false';
        }

        item.classList.toggle('mark',item.box.checked);

		// on change, either call a custom handler, or the
		// default option handler
		item.addEventListener('change',function( _event ){
			if ( this.id in handlers){ handlers[this.id]( this );}
			else { handlers.default( this ); }
		});
	}
	// define handlers for changing values
	var handlers = {

		// the function sets all other options to the same value
		// as the calling function, used by 'all'.
		all_label:function( button ){
			opts.forEach(function( item ){ item.box.checked = button.box.checked; });
            this.update();
		},

		// this function updates 'all' on the status of the other
		// options. (if they're all checked = set 'all' true, else
		// false)
		default:function( button ){
			all.box.checked = opts.every(function( item ){ return item.box.checked });
            this.update();
		},

		// called on every change to update the mark class on each
		// option so that styles apply.
		update:function(){
			for( var i=0 ; i<buttons.length ; i++ ){
				var item = buttons[i];
				item.classList.toggle('mark',item.box.checked);
                window.sessionStorage.setItem(item.box.id,item.box.checked);
			}
		}
	}

})(document.getElementsByClassName('option-item'));

/* -----------------------------------------------------------------------------
	SAVE INPUTS

		This immediately invoked anonymous function operates over inputs
		in the left-side menu of the index and about pages and does the
		following:

		1.	If the input has a value stored in sessionStorage, set it to that
            value, otherwise leave it.

		2.	Adds an 'onchange' eventlistener that saves the changed value into
			sessionStorage whenever it changes.
*/
(function( inputs ){
    for(var i=0; i <inputs.length;i++){
        var item = inputs[i];

        // if the input is already in sessionStorage
        // we load that value, otherwise we save the
        // starting value.
        if(item.id in sessionStorage){
            item.value = sessionStorage.getItem(item.id);
        } else {
            sessionStorage.setItem(item.id,item.value);
        }
        item.addEventListener('change',function( _event ){
            if(this.id){
                sessionStorage.setItem(this.id,this.value);
            }
        });
    }
})(document.querySelectorAll('input[type="text"], input[type="number"], select'));

/* -----------------------------------------------------------------------------
	DATE

		Sets the date in the copyright notice
*/
(function( block ){
    if(block){
        block.innerHTML = (new Date()).getFullYear();
    }
})(document.getElementById('js-year'));

/* -----------------------------------------------------------------------------
	HEIGHT ANIMATION

		Waits a moment, and then changes the min height of
        the sources block so that the tranition plays.
*/
/*
(function( target ){
    if(target){
        setTimeout(function(){
            target.style.minHeight = "10px";
        }, 500);
    }
})(document.getElementById('js-fit-height'));
*/
/* -----------------------------------------------------------------------------
	MOBILE MENU

		This bit adds a 'click' eventlistener that toggles the tabs and
		hides/displays the mobile menu. Tabs define functions to run from
		handlers with the 'run' attribute.
*/
(function( menu, options ){
	var tabs = [];
	[].push.apply(tabs, menu.getElementsByTagName('div'));

	var handlers = {
		open_menu:function(){options.classList.add('open')},
		close_menu:function(){options.classList.remove('open')},
	}

	tabs.forEach(function( tab ){
		tab.addEventListener('click',function( _event ){
			if(!this.classList.contains('current')){
				tabs.forEach(function(i){i.classList.remove('current')})
				this.classList.add('current');
				handlers[this.getAttribute('run')]();
			}
		})
	});
})(
	document.getElementById('js-mobile-menu'),
	document.getElementById('js-menu')
);
