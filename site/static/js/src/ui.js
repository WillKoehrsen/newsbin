
/* -----------------------------------------------------------------------------
	TOOLTIPS

		This immediately invoked function adds event listeners that create
        and destroy tooltips on elements with the 'tooltip="<message>"'
        attribute/value. They have the following features.

        1.  all tooltips have the class 'tooltip'

        2.  tooltips are oriented relative to the target element

        3.  if the left side of the target element is to the right of
            the viewport center, then the tooltip will be on the left,
            otherwise it will default to the right.
*/
var tooltips = (function( targets ){
    // function that actually adds the tooltip
    function make_tooltip( element ){
            var tooltip = null;
            var offset = 10;

            element.addEventListener('mouseover',function( _event ){
                var popup = document.createElement('div');
                tooltip = popup;
                popup.classList.add("tooltip");
                popup.classList.add( _event.target.getAttribute('tooltip-apply') )
                var msg = _event.target.getAttribute('tooltip');
                if(msg){
                    popup.innerHTML = msg;
                    document.body.appendChild(popup);

                    // move to where the tooltip should display
                    var reference = _event.target.getBoundingClientRect();
                    var right_ref = parseInt(reference.right);
                    var left_ref = parseInt(reference.left);

                    popup.style.left = right_ref+window.pageXOffset+offset+'px'
                    popup.style.top = parseInt(reference.top) + window.pageYOffset + 'px';
                }
            });

            element.addEventListener('mouseout',function( _event ){
                if(tooltip && tooltip.parentNode){
                    tooltip.parentNode.removeChild(tooltip);
                }
                tooltip = null;
            });
    }

    // handler
    handler = {
        add:function( item ){
            if(item.hasAttribute('tooltip')){
                make_tooltip( item );
            }
        }
    }

    for( var i = 0; i < targets.length; i++ ){
        make_tooltip( targets[i] );
    }

    return handler;
})(document.querySelectorAll('[tooltip]'));

function expand( element ){
    element.classList.toggle('active');
    var others = document.getElementsByClassName('active');
    for(var i = 0; i < others.length; i++ ){
        var item = others[i];
        if(item!=element){
            item.classList.remove('active');
        }
    }
}
