() => {
 const panel=()=>document.getElementById('mc-demo');
 const clamp=()=>{const p=panel();if(!p||!p.classList.contains('mc-open'))return;const r=p.getBoundingClientRect();p.style.left=Math.max(8,Math.min(r.left,innerWidth-r.width-8))+'px';p.style.top=Math.max(8,Math.min(r.top,innerHeight-r.height-8))+'px';p.style.right='auto';p.style.bottom='auto';};
 window.mcDemoToggle=(force)=>{const p=panel();if(!p)return;p.classList.toggle('mc-open',typeof force==='boolean'?force:!p.classList.contains('mc-open'));requestAnimationFrame(clamp);};
 if(window.mcUIAbort)window.mcUIAbort.abort();const ctrl=new AbortController();window.mcUIAbort=ctrl;const options={signal:ctrl.signal};
 document.addEventListener('keydown',e=>{if(e.altKey&&e.shiftKey&&e.code==='KeyD'){e.preventDefault();window.mcDemoToggle();}if(e.code==='Escape')window.mcDemoToggle(false);},options);
 let drag=null;
 document.addEventListener('pointerdown',e=>{if(!e.target.closest('#mc-drag'))return;const p=panel(),r=p.getBoundingClientRect();drag={x:e.clientX-r.left,y:e.clientY-r.top};e.preventDefault();},options);
 document.addEventListener('pointermove',e=>{if(!drag)return;const p=panel();p.style.left=Math.max(8,Math.min(e.clientX-drag.x,innerWidth-p.offsetWidth-8))+'px';p.style.top=Math.max(8,Math.min(e.clientY-drag.y,innerHeight-p.offsetHeight-8))+'px';p.style.right='auto';p.style.bottom='auto';},options);
 document.addEventListener('pointerup',()=>drag=null,options);window.addEventListener('resize',clamp,options);
}
