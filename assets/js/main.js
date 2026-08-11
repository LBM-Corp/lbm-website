/* LBM Corporation — site behaviour. No dependencies. */
(function () {
  'use strict';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- header ---------- */
  var hdr = $('.hdr');
  var top = $('.totop');
  function onScroll() {
    var y = scrollY;
    if (hdr) hdr.classList.toggle('is-stuck', y > 40);
    if (top) top.classList.toggle('is-on', y > 900);
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  var burger = $('.burger');
  if (burger) burger.addEventListener('click', function () {
    document.body.classList.toggle('nav-open');
  });
  $$('.nav a').forEach(function (a) {
    a.addEventListener('click', function () { document.body.classList.remove('nav-open'); });
  });
  if (top) top.addEventListener('click', function () {
    scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
  });

  /* ---------- brand mega panel ---------- */
  var megaBtn = $('.nav__brands'), mega = $('#mega'), megaHost = $('.nav__has'), megaT;
  if (megaBtn && mega) {
    var openMega = function () {
      clearTimeout(megaT);
      mega.hidden = false;
      requestAnimationFrame(function () { mega.classList.add('is-open'); });
      megaBtn.setAttribute('aria-expanded', 'true');
    };
    var closeMega = function (now) {
      clearTimeout(megaT);
      megaT = setTimeout(function () {
        mega.classList.remove('is-open');
        megaBtn.setAttribute('aria-expanded', 'false');
        setTimeout(function () { if (!mega.classList.contains('is-open')) mega.hidden = true; }, 400);
      }, now ? 0 : 160);
    };
    [megaHost, mega].forEach(function (el) {
      if (!el) return;
      el.addEventListener('mouseenter', openMega);
      el.addEventListener('mouseleave', function () { closeMega(); });
    });
    megaBtn.addEventListener('click', function (ev) {
      if (mega.classList.contains('is-open')) return;   /* second click follows the link */
      ev.preventDefault(); openMega();
    });
    megaBtn.addEventListener('focus', openMega);
    addEventListener('keydown', function (ev) { if (ev.key === 'Escape') closeMega(true); });
    addEventListener('scroll', function () {
      if (mega.classList.contains('is-open')) closeMega(true);
    }, { passive: true });
  }

  /* ---------- brand sub-nav: highlight the section in view ---------- */
  var subs = $$('.subnav a[href^="#"]');
  if (subs.length && 'IntersectionObserver' in window) {
    var targets = subs.map(function (a) { return document.getElementById(a.hash.slice(1)); }).filter(Boolean);
    var sn = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        subs.forEach(function (a) { a.classList.toggle('is-on', a.hash === '#' + en.target.id); });
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    targets.forEach(function (t) { sn.observe(t); });
  }

  /* ---------- reveal on scroll ---------- */
  var rise = $$('[data-rise]');
  function revealAll() { rise.forEach(function (el) { el.classList.add('is-in'); }); }
  setTimeout(revealAll, 2600);          /* safety net — content is never stuck hidden */
  if (rise.length) {
    if (!('IntersectionObserver' in window) || reduce) {
      rise.forEach(function (el) { el.classList.add('is-in'); });
    } else {
      var ro = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          var d = parseFloat(e.target.getAttribute('data-rise')) || 0;
          e.target.style.transitionDelay = d + 'ms';
          e.target.classList.add('is-in');
          ro.unobserve(e.target);
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
      rise.forEach(function (el) { ro.observe(el); });
    }
  }

  /* ---------- slow image rotation ----------
     Board note: v1 held 3s. This holds HOLD ms per frame and cross-fades
     over 3.4s (CSS), with each panel offset so they never turn together. */
  /* Board note: v1 held 3s. Holds are long here, but the FIRST turn comes
     quickly so the rotation is visibly alive. Driven by elapsed time rather
     than raw intervals, so a backgrounded or throttled tab resumes correctly
     instead of silently dropping every tick. */
  /* Panels turn as a wave: left to right, one after another, then the
     whole row rests. Independent per-panel timers drifted out of order —
     one controller keeps the sweep in sequence. */
  var HOLD = 15000, STEP = 1800, FIRST = 5000;

  function panelFrames(panel) {
    var imgs = $$('img', panel), cap = $('.hero__cap', panel);
    if (!imgs.length) return null;
    imgs[0].classList.add('is-on');
    return { imgs: imgs, cap: cap, i: 0 };
  }

  function advance(p) {
    if (p.imgs.length < 2) return;
    p.imgs[p.i].classList.remove('is-on');
    p.i = (p.i + 1) % p.imgs.length;
    p.imgs[p.i].classList.add('is-on');
    if (p.cap) {
      p.cap.style.opacity = 0;
      setTimeout(function () {
        p.cap.textContent = p.imgs[p.i].getAttribute('data-cap') || '';
        p.cap.style.opacity = '';
      }, 700);
    }
  }

  /* Each panel keeps its own next-turn time on one shared clock, offset by
     STEP and advanced by exactly HOLD. The previous loop added the whole
     stagger to the cycle length (so the row turned in a clump and then sat
     still for 16.8s), measured the next turn from whichever frame happened
     to fire (so it drifted later every cycle), and queued each turn on its
     own setTimeout (so a busy or throttled tab delivered them out of order). */
  var wave = $$('.hero__panel').map(panelFrames).filter(Boolean);
  if (wave.length && !reduce) {
    var t0 = performance.now() + FIRST;
    wave.forEach(function (p, n) { p.next = t0 + n * STEP; });
    (function tick(now) {
      for (var k = 0; k < wave.length; k++) {
        var p = wave[k];
        if (now >= p.next) {
          advance(p);
          p.next += HOLD;
          if (now - p.next > HOLD) {
            p.next += Math.ceil((now - p.next) / HOLD) * HOLD;
          }
        }
      }
      requestAnimationFrame(tick);
    })(performance.now());
  }

  function rotate(panel, offset) {
    var p = panelFrames(panel);
    if (!p || p.imgs.length < 2 || reduce) return;
    var next = performance.now() + offset + FIRST;
    (function tick(now) {
      if (now >= next) { advance(p); next = now + HOLD; }
      requestAnimationFrame(tick);
    })(performance.now());
  }
  $$('.bhero__panel').forEach(function (p) { rotate(p, 0); });

  /* ---------- index rail highlight ---------- */
  var dexEl = $('.dex');
  if (dexEl) {
    var dexToggle = function () { dexEl.classList.toggle('is-on', scrollY > innerHeight * 0.86); };
    addEventListener('scroll', dexToggle, { passive: true }); dexToggle();
  }
  var dex = $$('.dex a');
  if (dex.length && 'IntersectionObserver' in window) {
    var secs = dex.map(function (a) { return document.getElementById(a.hash.slice(1)); }).filter(Boolean);
    var so = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        dex.forEach(function (a) { a.classList.toggle('is-on', a.hash === '#' + e.target.id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    secs.forEach(function (s) { so.observe(s); });
  }

  /* ---------- scramble type ----------
     Brand-sourced: the six MOOD words from the London Bagel Museum brand deck.
     Letters resolve left-to-right out of noise. Korean scrambles within
     Hangul syllables so it never renders as mojibake. */
  var LAT = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
  function noiseFor(ch) {
    var c = ch.charCodeAt(0);
    if (c >= 0xAC00 && c <= 0xD7A3) return String.fromCharCode(0xAC00 + Math.floor(Math.random() * 11172));
    if (/[A-Za-z]/.test(ch)) return LAT[Math.floor(Math.random() * LAT.length)];
    return ch;
  }
  function scramble(el) {
    var target = el.getAttribute('data-scramble');
    var chars = Array.from(target);
    var frame = 0, done = 0;
    var slots = chars.map(function (ch, i) {
      return { ch: ch, start: Math.floor(i * 2.2) + 2, end: Math.floor(i * 2.2) + 14 + Math.floor(Math.random() * 12) };
    });
    el.classList.add('is-idle');
    (function tick() {
      var out = '', settled = 0;
      slots.forEach(function (s) {
        if (frame >= s.end) { out += s.ch; settled++; }
        else if (frame >= s.start) { out += (s.ch === ' ') ? ' ' : noiseFor(s.ch); }
        else { out += ' '; }
      });
      el.textContent = out;
      frame++;
      if (settled === slots.length) { el.classList.remove('is-idle'); return; }
      requestAnimationFrame(tick);
    })();
  }
  var moods = $$('[data-scramble]');
  if (moods.length) {
    if (reduce) {
      moods.forEach(function (el) { el.textContent = el.getAttribute('data-scramble'); });
    } else {
      var mo = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          var t = e.target, d = parseInt(t.getAttribute('data-delay') || '0', 10);
          t.textContent = '';
          setTimeout(function () { scramble(t); }, d);
          mo.unobserve(e.target);
        });
      }, { threshold: 0.5 });
      moods.forEach(function (el) { mo.observe(el); });
    }
  }

  /* ---------- location thumbs swap the primary shot ---------- */
  $$('.loc, .strow').forEach(function (loc) {
    var main = $('.loc__main', loc);
    if (!main) return;
    var first = main.getAttribute('src');
    var firstSet = main.getAttribute('srcset');
    var thumbs = $$('.loc__strip button, .strow__thumbs button', loc);
    thumbs.forEach(function (btn) {
      function show() {
        main.setAttribute('src', btn.getAttribute('data-full'));
        main.removeAttribute('srcset');
        thumbs.forEach(function (b) { b.removeAttribute('aria-current'); });
        btn.setAttribute('aria-current', 'true');
      }
      btn.addEventListener('mouseenter', show);
      btn.addEventListener('focus', show);
      btn.addEventListener('click', function (ev) { ev.preventDefault(); show(); });
    });
    loc.addEventListener('mouseleave', function () {
      main.setAttribute('src', first);
      if (firstSet) main.setAttribute('srcset', firstSet);
      thumbs.forEach(function (b) { b.removeAttribute('aria-current'); });
    });
  });

  /* ---------- quotes: words assemble into place ----------
     The board asked for words drifting and resolving. This is that idea
     applied where it reads as intent rather than decoration: each word
     lifts out of a blur and settles, left to right. */
  var quotes = $$('.quote blockquote, .band--quote blockquote');
  if (quotes.length && !reduce) {
    quotes.forEach(function (bq) {
      if (bq.dataset.split) return;
      bq.dataset.split = '1';
      var html = bq.textContent.split('\n').map(function (line) {
        return line.split(/\s+/).filter(Boolean).map(function (w) {
          return '<span class="wd"><i>' + w + '</i></span>';
        }).join(' ');
      }).join('<br>');
      bq.innerHTML = html;
    });
    if ('IntersectionObserver' in window) {
      var qo = new IntersectionObserver(function (es) {
        es.forEach(function (en) {
          if (!en.isIntersecting) return;
          $$('.wd i', en.target).forEach(function (w, n) {
            w.style.transitionDelay = (n * 65) + 'ms';
          });
          en.target.classList.add('is-set');
          qo.unobserve(en.target);
        });
      }, { threshold: 0.35 });
      quotes.forEach(function (q) { qo.observe(q); });
    } else {
      quotes.forEach(function (q) { q.classList.add('is-set'); });
    }
  }

  /* ---------- instagram ----------
     Renders data/site.json → instagram.posts. Pinned first, then newest.
     Empty array renders the follow card instead of a broken grid. */
  var igMount = $('[data-ig]');
  if (igMount) {
    fetch(igMount.getAttribute('data-ig-src') || '../data/site.json')
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var handle = igMount.getAttribute('data-ig');
        var posts = ((d.instagram && d.instagram.posts) || []).filter(function (p) {
          return !p.brand || p.brand === handle;
        });
        if (!posts.length) return;
        posts.sort(function (a, b) {
          if (!!b.pinned - !!a.pinned) return !!b.pinned - !!a.pinned;
          return new Date(b.timestamp || 0) - new Date(a.timestamp || 0);
        });
        igMount.innerHTML = posts.slice(0, 12).map(function (p) {
          return '<a class="ig__i" href="' + p.permalink + '" target="_blank" rel="noopener">' +
            '<img loading="lazy" src="' + p.image + '" alt="' +
            String(p.caption || '').replace(/"/g, '&quot;').slice(0, 110) + '">' +
            (p.pinned ? '<span class="ig__pin">Pinned</span>' : '') + '</a>';
        }).join('');
        igMount.hidden = false;
        var ph = $('[data-ig-empty]');
        if (ph) ph.hidden = true;
      })
      .catch(function () { /* keep the follow card */ });
  }
})();


/* Whole index row is clickable, not only the title. The <a> stays in the
   markup so keyboard and middle-click still work. */
(function () {
  var rows = document.querySelectorAll('.ix__t8 tbody tr[data-cat]');
  [].forEach.call(rows, function (r) {
    r.addEventListener('click', function (ev) {
      if (ev.target.closest('a')) return;
      var a = r.querySelector('.ix__t a');
      if (a) window.location = a.href;
    });
  });
})();

/* Newsroom 분류 filter (22). With JS off every row still renders. */
(function () {
  var sel = document.getElementById('catfilter');
  if (!sel) return;
  var rows = [].slice.call(document.querySelectorAll('.ix__t8 tbody tr[data-cat]'));
  var count = document.querySelector('.ix__count b');
  sel.addEventListener('change', function () {
    var v = sel.value, n = 0;
    rows.forEach(function (r) {
      var on = v === 'all' || r.getAttribute('data-cat') === v;
      r.hidden = !on;
      if (on) n++;
    });
    if (count) count.textContent = n;
  });
})();
