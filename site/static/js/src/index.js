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
		This function handles the menus
*/
(function( menus ){
    function load( item ){
        if(item.id in sessionStorage){ return sessionStorage.getItem(item.id)!='false'; }
        else                         { return item.checked; }
    }

    for(var i = 0; i < menus.length; i++){
        var menu = menus[i];

        // handler for each menu
        (function( all, opts ){
            var options = new Array();
            for(var i = 0; i < opts.length; i++)
                options.push(opts[i]);
            var all_options = new Array(all);
            all_options.push.apply(all_options,options);

            all_options.forEach(function(option){
                if(option){
                    option.box = option.getElementsByTagName('input')[0];
                    option.box.checked = load(option.box);
                    option.classList.toggle('mark',option.box.checked);

                    if(option==all){
                        option.addEventListener('change',function(_event){
                            var state = this.box.checked;
                            options.forEach(function( item ){ item.box.checked = state; });
                        });
                    }
                    else {
                        option.addEventListener('change',function(_event){
                            all.box.checked = options.every(function( item ){ return item.box.checked });
                        });
                    }

                    option.addEventListener('change',function(_event){
                        all_options.forEach(function(item){
                            item.classList.toggle('mark',item.box.checked);
                            window.sessionStorage.setItem(item.box.id,item.box.checked);
                        });
                    });
                }
            });
        })(
            menu.getElementsByClassName('all')[0],
            menu.getElementsByClassName('option')
        );
        // -----------------------
    }
})(document.getElementsByClassName('drop-down-menu'));

/* -----------------------------------------------------------------------------
	PRE-SUBMIT PROCESS FORM

        Organize info from the form into a more condensed url before
        submit. Each collection of checkboxes gets turned into a
        string of a values like so:
            value1=on value2=on value3=off
                becomes
            values=value1,value2
*/
(function( form ){
    function process(_event){
        _event.preventDefault();
        var categories = form.querySelectorAll('.categories .option>input[type=checkbox]');
        var sources = form.querySelectorAll('.sources .option>input[type=checkbox]');

        var cat_arr = new Array();
        var src_arr = new Array();

        for(var i = 0; i < sources.length; i++){
            var item = sources[i];
            if(item.checked){
                src_arr.push(item.getAttribute('no-name'));
            }
        }

        for(var i = 0; i < categories.length; i++){
            var item = categories[i];
            if(item.checked){
                cat_arr.push(item.getAttribute('no-name'));
            }
        }

        document.getElementById('js-sources-str').value = src_arr.join('|');
        document.getElementById('js-categories-str').value = cat_arr.join('|');

        form.submit();
        return false;
    }

    try     {form.addEventListener("submit", process, false);}
    catch(e){form.attachEvent("onsubmit", process);}

})(document.getElementById('js-submit'));

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
	INFINITE SCROLL

		When the viewer gets close to the bottom of the page, we add new content
*/
(function( list ){
    // function-global variables
    var articles = []
    var fetching = false;
    var the_end = false;
    var end_msg = 'no more articles here, sorry :/';

    var page = window.location.search.match( /page=(.*?)(&|\/|$)/ );
    if(page != null){ page = parseInt(page[1]); }
    else { page = 0; }

    // functions
    function fetch_next_page(){
        if(!fetching){
            fetching = true;
            page = page+1;
            var handle = new XMLHttpRequest();
            handle.onload = function(){
                if(this.status==200){
                    var response = JSON.parse(this.responseText);
                    for( var i = 0; i < response.length; i++ ){
                        var article = response[i];
                        astr =  '<div class="category">'+ article.category_label +'</div>' +
                                '<a class="title" href="/articles/'+ article.id +'/" target="_blank">'+ article.title +'</a>' +
                                '<div class="date-source"><a class="source" href="'+ article.link +'" target="_blank" rel="noopener">'+ article.source_label +'</a>' +
									 ' on '+ article.fetched.split(' ')[0] +'</div>';

                        aobj = document.createElement('div');
                        aobj.classList.add("titlecard");
                        aobj.innerHTML = astr;
                        articles.push(aobj);
                    }
                    update_url( page );
                }
                else {
                    var endblock = document.createElement('div');
                    endblock.classList.add('the-end');
                    endblock.innerHTML = end_msg;
                    list.appendChild(endblock);
                    the_end = true;
                }

                fetching = false;
            }
            handle.open("GET", '/articles/?page=' + page + '&next', true);
            handle.send();
        }
    }

    function update_url( num ){
        var sobj = {};
        var search = window.location.search;
        if(search){
            if(search.indexOf('page') == -1){
                search = search.replace(/(\&+|\/+)$/, '') + '&page=' + num;
            }
            else {
                search = search.replace(/page=.*?(&|\/|$)/,'page='+ num +'$1')
            }
        }
        else {
            search = '?page=' + num;
        }
        history.replaceState(sobj, "page " + num, search);
    }

    function load_next_card(){
        if(!the_end){
            if(articles.length == 0){
                fetch_next_page();
            }
            // we have articles we can insert
            var timed = window.setInterval(function(){
                if(articles.length > 0){
                    var article = articles.shift();
                    list.appendChild(article);
                }
                else {
                    window.clearInterval(timed);
                }
            },250);
        }
    }

    function get_scroll_position(){
        var pos     = window.pageYOffset + window.innerHeight;
        var bottom  = document.body.offsetHeight;
        return bottom-pos;
    }

    // triggering event
	window.addEventListener('scroll',function( _event ){
        var remaining = get_scroll_position();
        if(remaining<100){
            load_next_card();
        }
    });
})(document.getElementById('js-titlecard-list'));
