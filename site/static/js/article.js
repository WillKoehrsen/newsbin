NodeList.prototype.forEach||(NodeList.prototype.forEach=function(t,e){for(var n=0,a=this.length;n<a;++n)t.call(e,this[n],n,this)});var modal=function(t){t.refs={};for(var e=t.getElementsByTagName("div"),n=0;n<e.length;n++){var a=e[n].getAttribute("ref");a&&(t.refs[a]=e[n])}return handlers={close:function(){for(a in t.refs)t.refs[a].innerHTML="";t.style.display="none"},open:function(e){var n=new XMLHttpRequest,a=t.refs;n.onload=function(){if(200==this.status){handlers.close();var e=JSON.parse(this.responseText);a.close.innerHTML="Close",a.title.innerHTML=e.name,a.image.innerHTML='<img src="'+e.image+'"/>',e.summary.split("\n\n").forEach(function(t){a.content.innerHTML+="<p>"+t+"</p>"}),a.links.innerHTML+='<a href="https://en.wikipedia.org/wiki/'+e.name+'" target="_blank">on wikipedia</a>',e.slug&&(a.links.innerHTML+='<a href="http://www.politifact.com/personalities/'+e.slug+'" target="_blank">on politifact</a>'),e.data_table.forEach(function(t){a.data.innerHTML+='<div class="modal-data-item" tooltip="'+t.tooltip+'">\t\t\t\t\t\t\t\t\t\t\t\t\t<div>'+t.key+"</div>\t\t\t\t\t\t\t\t\t\t\t\t\t<div>"+t.value+"</div>\t\t\t\t\t\t\t\t\t\t\t\t</div>",tooltips.add(a.data.lastChild)}),t.style.display="flex"}else console.log(this.status)},n.open("GET","/annotations?name="+e,!0),n.send()}},handlers}(document.getElementById("js-modal-annotation")),annotations=function(){function t(t){e&&modal.open(this.getAttribute("name"))}var e=!0,n={disable:function(){e=!1;for(var t=document.getElementsByClassName("annotation"),n=0;n<t.length;n++)t[n].classList.remove("highlight")},enable:function(){e=!0;for(var t=document.getElementsByClassName("annotation"),n=0;n<t.length;n++)t[n].classList.add("highlight")},refresh:function(){for(var e=document.getElementsByClassName("annotation"),n=document.getElementById("js-eye-toggle"),a=0;a<e.length;a++){var o=e[a];o.removeEventListener("click",t,!1),o.addEventListener("click",t),n.classList.contains("active-toggle")&&o.classList.add("highlight")}}};return n.refresh(),n.enable(),n}();!function(t,e){t&&t.addEventListener("mouseup",function(){var t=window.getSelection();if(!t.isCollapsed&&1==t.rangeCount){var n=t.getRangeAt(0);e&&n&&(e.value=n.toString())}})}(document.getElementById("js-article-content"),document.getElementById("js-add-selection")),function(t){t&&(t.innerHTML=(new Date).getFullYear())}(document.getElementById("js-year")),function(t,e){t&&e&&(t.id in sessionStorage&&("false"!=sessionStorage.getItem(t.id)?(t.classList.add("active-toggle"),annotations.enable()):(t.classList.remove("active-toggle"),annotations.disable())),e.addEventListener("click",function(){t.classList.toggle("active-toggle")?(annotations.enable(),window.sessionStorage.setItem(t.id,!0)):(annotations.disable(),window.sessionStorage.setItem(t.id,!1))}))}(document.getElementById("js-eye-toggle"),document.getElementById("js-eye-btn")),function(t){function e(t,n){if("A"!=t.tagName){for(var a="",o=0;o<t.childNodes.length;o++){var i=t.childNodes[o];switch(i.nodeType){case 1:i.innerHTML=e(i,n),a+=i.outerHTML;break;case 3:var s=new RegExp(n.join("|"),"g");a+=i.nodeValue.replace(s,function(t,e,n){return'<span class="annotation" name="'+t+'">'+t+"</span>"})}}return a}return t.outerHTML}var n=new XMLHttpRequest;n.onload=function(){if(200==this.status)try{var n=JSON.parse(this.responseText).annotations.sort(function(t,e){return e.length-t.length||t.localeCompare(e)});console.log(n),t.innerHTML=e(t,n),annotations.refresh()}catch(t){console.log(t)}},n.open("GET","/article/"+DATA.id+"/annotate",!0),n.send()}(document.getElementById("js-article-content"));