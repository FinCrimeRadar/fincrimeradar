/* FinCrimeRadar brand layer: scroll reveals.
   Conservative by design: content is fully visible without JS,
   reveal classes are only applied when IO is supported and the
   user has not requested reduced motion. */
(function(){
  "use strict";
  if(!('IntersectionObserver' in window)) return;
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var revealThreshold = 0.08;
  var revealBottomMargin = 30;
  var targets = document.querySelectorAll(
    'main section, [class*="card"], .footer-col, footer > div'
  );
  if(!targets.length) return;

  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting){
        en.target.classList.add('in');
        io.unobserve(en.target);
      }
    });
  },{
    threshold:revealThreshold,
    rootMargin:'0px 0px -' + revealBottomMargin + 'px 0px'
  });

  var vh = window.innerHeight;
  var maxRevealHeight = Math.max(0, vh - revealBottomMargin) / revealThreshold;
  var stagger = 0;
  targets.forEach(function(el){
    var r = el.getBoundingClientRect();
    /* Never hide anything already on screen at load: no flash, no jank */
    if(r.top < vh && r.bottom > 0) return;
    if(r.height < 8) return;
    /* Keep targets visible when their height cannot satisfy the IO threshold. */
    if(r.height > maxRevealHeight) return;
    el.style.setProperty('--brv-delay', ((stagger++ % 4) * 0.07) + 's');
    /* Register observation before hiding so an observe failure leaves content visible. */
    io.observe(el);
    el.classList.add('brv');
  });
})();

/* Table overflow fix, second attempt.
   Forcing display:block directly on the table element did not
   reliably create a scrollable container on the live device it was
   tested against, a known inconsistency with that technique across
   browsers. Wrapping the table in a genuine block level div is the
   reliable version of this fix, so this runs on every page and
   physically wraps any comparison table in a scrollable container
   rather than relying on the table's own display mode.
   table.ref-table is the locked "At a glance" reference table used
   as every guide's end-of-guide visual summary (see BACKLOG.md
   Content Loop standing requirement): it overflowed uncontrolled on
   mobile, invisible and unreachable, because it wasn't in this list.
   Any future guide built against that standard must keep the
   ref-table class so it picks up this wrapper automatically. */
(function(){
  "use strict";
  var tables = document.querySelectorAll('table.data-table, table.compare-table, table.ref-table');
  tables.forEach(function(t){
    if(t.parentElement && t.parentElement.classList.contains('table-scroll')) return;
    var wrap = document.createElement('div');
    wrap.className = 'table-scroll';
    wrap.style.overflowX = 'auto';
    wrap.style.webkitOverflowScrolling = 'touch';
    wrap.style.maxWidth = '100%';
    t.parentNode.insertBefore(wrap, t);
    wrap.appendChild(t);
  });
})();
