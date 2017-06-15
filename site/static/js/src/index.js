// -----------------------------------------------------------------------------
// implement forEach if we're in IE
if (!NodeList.prototype.forEach) {
    NodeList.prototype.forEach = function(fn, scope) {
        for(var i = 0, len = this.length; i < len; ++i) {
            fn.call(scope, this[i], i, this);
        }
    }
}

var storage = new Vue();

var options = new Vue({
	el: '#js-sidebar-form',
	components: {
		'x-option':{
			template:"<label :class='{ mark: checked }'>{{ label }}<input v-model='checked' type='checkbox' v-on:change='crybaby' :name='name' style='display:none;'></label>",
			props:['value','label','name'],
			data:function(){return { checked:true }},
			methods:{
				crybaby:function( event ){
                    this.$emit('toggled',this);
                },
                set:function( value ){
                    this.$data.checked = value;
                }
			},
		},
	},
	data: {
		checkboxes:[
            { name:'all', label:'All', checked:true },
            { name:'cnn', label:'CNN', checked:true },
            { name:'cnbc', label:'CNBC', checked:true },
            { name:'foxnews', label:'Fox News', checked:true },
            { name:'nytimes', label:'New York Times', checked:true },
            { name:'reuters', label:'Reuters', checked:true },
            { name:'washingtonpost', label:'Washington Post', checked:true },
        ],
		category:'',
		search:'',
		count:'',
		active:false,
	},
	methods: {
        notify:function( caller ){
            if(caller.name=='all'){
                this.set_all( caller );
            } else {
                this.update( caller );
            }
        },
		set_all:function( caller ){
            this.$children.forEach(function(item){
                if(item.$options._componentTag=='x-option'){
                    item.checked = caller.checked;

                    // update the local value of each checkbox
                    window.sessionStorage[item.name] = item.checked;
                }
            });
		},
		update:function( caller ){
            // store the checkbox value locally
            window.sessionStorage[caller.name] = caller.checked;

            var options = this.$children.filter(function( item ){ return (item.$options._componentTag=='x-option') });
            var all = options[0];
            var children = options.slice(1);
            for(var i = 0; i < children.length; i++){
                var item = children[i];
                if(!item.checked){
                    all.checked = false;
                    window.sessionStorage[all.name] = all.checked;
                    return;
                }
            }
            all.checked = true;
            window.sessionStorage[all.name] = all.checked;
		},
        reload:function(){
            this.$children.forEach(function(item){
                if(item.$options._componentTag=='x-option'){
                    console.log('setting ' + item.name + '.checked to ' + window.sessionStorage[item.name]);
                    item.$data.checked = window.sessionStorage[item.name];
                }
            });
        },
        open: function(){
			this.active = true;
		},
		close: function(){
			this.active = false;
		},
	},
});

var titles = new Vue({
	el: '#js-titlecard-list',
	components: {
		'x-titlecard':{
			template:'<div class="titlecard">\
                            <a :href="link" class="title-link">{{ title }}</a>\
                            <table class="information">\
                                <tr>\
                                <td><a :href="original" target="_blank">on {{ source }}</a></td>\
                                <td>author: {{ author ? author : "unknown" }}</td>\
                                <td>fetched: {{ date }}</td>\
                                </tr>\
                            </table>\
                      </div>',
			props:['title','link','source','original','author','date'],
			data:function(){return { }},
			methods:{
				notify:function( event ){
                    this.$emit('toggled',this);
                },
			},
		},
	},
	data: {
	},
	methods: {
	},
});

var mobile = new Vue({
	el: '#js-mobile-menu',
	data:{
		article: true,
		menu: false,
	},
	methods: {
		toggle: function( event ){
			this.article = this.menu;
			if(this.menu = !this.menu){
				options.open();
			} else {
				options.close();
			}
		},
	},
});

(function( block ){
    if(block){
        block.innerHTML = (new Date()).getFullYear();
    }
})(document.getElementById('js-year'));

(function( target ){
    if(target){
        setTimeout(function(){
            target.style.minHeight = "10px";
        }, 500);
    }
})(document.getElementById('js-fit-height'));
