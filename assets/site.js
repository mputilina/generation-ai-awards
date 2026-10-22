/* Generation AI Awards — shared behaviour for inner pages */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* mobile menu */
  const burger = $('.burger');
  if (burger) {
    burger.addEventListener('click', () => {
      const open = document.body.classList.toggle('menu-open');
      burger.setAttribute('aria-expanded', open);
    });
    $$('.nav a').forEach(a => a.addEventListener('click', () => document.body.classList.remove('menu-open')));
  }

  /* wrap wide tables so they scroll on phones */
  $$('.prose table').forEach(t => {
    const w = document.createElement('div'); w.className = 'tbl';
    t.parentNode.insertBefore(w, t); w.appendChild(t);
  });

  /* side contents: the link of the section you are reading turns lime */
  const side = $('.art-side');
  if (side) {
    const links = $$('a[href^="#"]', side), heads = links.map(a => document.getElementById(decodeURIComponent(a.hash.slice(1)))).filter(Boolean);
    const spy = () => { let cur = heads[0]; heads.forEach(h => { if (h.getBoundingClientRect().top < innerHeight * .3) cur = h; });
      links.forEach(a => a.classList.toggle('on', decodeURIComponent(a.hash.slice(1)) === cur.id)); };
    addEventListener('scroll', spy, {passive: true}); spy();
  }

  /* gallery lightbox */
  const lb = $('#lb');
  if (lb) {
    const shots = $$('.ggrid button');
    const img = $('img', lb);
    let i = 0;
    const show = n => { i = (n + shots.length) % shots.length; img.src = shots[i].dataset.full; img.alt = $('img', shots[i]).alt; };
    shots.forEach((b, n) => b.addEventListener('click', () => { show(n); lb.classList.add('open'); $('.x', lb).focus(); }));
    $('.x', lb).addEventListener('click', () => lb.classList.remove('open'));
    $('.p', lb).addEventListener('click', () => show(i - 1));
    $('.n', lb).addEventListener('click', () => show(i + 1));
    lb.addEventListener('click', e => { if (e.target === lb) lb.classList.remove('open'); });
    addEventListener('keydown', e => {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') lb.classList.remove('open');
      if (e.key === 'ArrowLeft') show(i - 1);
      if (e.key === 'ArrowRight') show(i + 1);
    });
  }

  /* application forms.
     To make them send for real, put your form handler URL into data-endpoint
     on the <form> (for example a Tilda, Formspree or your own backend URL). */
  $$('form.appform').forEach(f => f.addEventListener('submit', async e => {
    e.preventDefault();
    const msg = $('.formmsg', f);
    const url = f.dataset.endpoint;
    if (!url) {
      msg.textContent = 'Форма заполнена корректно. Отправка заработает после подключения обработчика заявок (атрибут data-endpoint у формы).';
      msg.classList.add('show');
      return;
    }
    try {
      const r = await fetch(url, { method: 'POST', body: new FormData(f) });
      if (!r.ok) throw new Error(r.status);
      msg.textContent = 'Заявка отправлена. Оргкомитет свяжется с вами по указанному email.';
      f.reset();
    } catch (err) {
      msg.textContent = 'Заявка не отправилась. Проверьте подключение к интернету и попробуйте еще раз или напишите на genaiawards@generation-ai.ru.';
    }
    msg.classList.add('show');
  }));
})();

/* footer wordmark: shrink until the whole line fits (same as the main page) */
(() => {
  const h = document.querySelector('.ftr .huge'); if (!h) return;
  const fit = () => { h.style.fontSize = ''; let fs = parseFloat(getComputedStyle(h).fontSize);
    while (h.scrollWidth > h.clientWidth && fs > 20) { fs -= 1; h.style.fontSize = fs + 'px'; } };
  fit(); addEventListener('resize', fit); document.fonts && document.fonts.ready.then(fit);
})();
