#!/usr/bin/env python3
"""Builds every inner page of the Generation AI Awards site from data/ into out/.
Edit the files in data/, run `python3 build.py`, and all pages are regenerated
with the same header, footer and links."""
import html, re, pathlib, markdown
from markdown.extensions.toc import slugify_unicode

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / 'data'
OUT = ROOT.parent
OUT.mkdir(exist_ok=True)
esc = html.escape

exec((DATA / 'noms.py').read_text(encoding='utf-8'))      # -> NOMS
NOM_BY = {n['slug']: n for n in NOMS}

def nom_file(slug): return f"nomination-{slug.replace('_', '-')}.html"

# order and titles exactly as on the main page
NOM_ORDER = ['best-project-in-genai', 'tech_scale', 'transformation', 'best_startup', 'best_inhouse_dev',
             'best_educational_project', 'contribution', 'best_client_solution', 'best_solution_marketing',
             'best_solution_hr', 'best_solution_tech', 'choice', 'ink']
NOM_TITLE = {**{n['slug']: n['title'] for n in NOMS},
             'choice': 'Выбор генеративного AI', 'ink': 'Спецприз от медиа для предпринимателей «Инк»'}

EXPERT_VIEW = 'https://generation-ai.ru/media/genai-awards-expert-view'

# Where "Заполнить заявку" leads. The live site hosts the working application forms.
APPLY_BASE = 'https://awards.generation-ai.ru/nomination/'

def header(active=''):
    cur = lambda k: ' aria-current="page"' if k == active else ''
    dd = lambda *ks: ' on' if active in ks else ''
    return f'''<header class="hdr" id="hdr">
  <a href="index.html" class="logo" aria-label="Generation AI Awards — на главную"><img src="assets/logo.svg" alt="Generation AI Awards" width="235" height="59"></a>
  <button class="burger" aria-label="Меню" aria-expanded="false"><i></i></button>
  <nav class="nav" aria-label="Основное меню">
    <a href="index.html#about"{cur('about')}>О премии</a><a href="index.html#nom"{cur('nom')}>Номинации</a>
    <div class="dd{dd('w26','w25')}"><button>Лауреаты<i></i></button><div class="sub"><a href="shortlist-2026.html"{cur('w26')}>2026 год</a><a href="shortlist-2025.html"{cur('w25')}>2025 год</a></div></div>
    <div class="dd{dd('g26','g25')}"><button>Галерея<i></i></button><div class="sub"><a href="gallery-2026.html"{cur('g26')}>2026 год</a><a href="gallery-2025.html"{cur('g25')}>2025 год</a></div></div>
    <div class="dd{dd('nav','rev')}"><button>Полезное<i></i></button><div class="sub wide">
      <a href="ai-navigator.html"{cur('nav')}><b>AI-Навигатор 2.0</b><span>Пошаговое руководство для оформления заявок</span></a>
      <a href="{EXPERT_VIEW}" target="_blank" rel="noopener"><b>Что думают члены жюри о будущем GenAI в России?</b><span>Взгляд AI-экспертов Generation AI Awards</span></a>
      <a href="analytical-review.html"{cur('rev')}><b>От чат-бота к агенту</b><span>Аналитический обзор по итогам 2026: тренды и отраслевые кейсы</span></a></div></div>
  </nav>
  <a href="shortlist-2026.html" class="btn ghost"><span class="long">Смотреть победителей</span><span class="short">Победители</span></a>
</header>'''

def main_footer():
    """The footer is read from index.html so every page shows exactly the main page's footer."""
    src = (OUT / 'index.html').read_text(encoding='utf-8')
    f = src[src.find('<footer'):src.find('</footer>') + 9]
    return f.replace('href="#about"', 'href="index.html#about"').replace('href="#nom"', 'href="index.html#nom"')
FOOTER = main_footer()

def crumbs(*items):
    parts = ['<a href="index.html">Премия</a>']
    for label, href in items:
        parts.append('<span aria-hidden="true">/</span>')
        parts.append(f'<a href="{href}">{esc(label)}</a>' if href else f'<span>{esc(label)}</span>')
    return '<nav class="crumbs" aria-label="Навигация">' + ''.join(parts) + '</nav>'

def page(fname, title, desc, body, active='', body_cls=''):
    doc = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
</head>
<body{f' class="{body_cls}"' if body_cls else ''}>
{header(active)}
{body}
{FOOTER}
<script src="assets/site.js"></script>
</body>
</html>
'''
    (OUT / fname).write_text(doc, encoding='utf-8')
    return fname

# ---------- markdown with a few site-specific blocks ----------
def logo_url(x): return x   # local path (images/logos/*.webp) or a full URL

# case-card logos (only «От чат-бота к агенту» has case cards): round images listed in data/case_logos.txt
CASE_LOGO = dict([x.strip() for x in ln.split('|')] for ln in (DATA / 'case_logos.txt').read_text(encoding='utf-8').split('\n')
                 if ln.strip() and not ln.startswith('#'))

def case_html(line):
    co, kind, task, sol, res, nom = [x.strip() for x in line[2:].split('|')]
    win = ' win' if 'победитель' in nom else ''
    lg = CASE_LOGO.get(co)
    initials = ''.join(w[0] for w in re.findall(r'[\wА-Яа-яЁё]+', co)[:2]).upper()
    lgh = (f'<img class="clogo" src="{lg}" alt="{esc(co)}" loading="lazy">' if lg
           else f'<span class="clogo none" aria-hidden="true">{esc(initials)}</span>')   # same circle when no logo yet
    return (f'<article class="case">{lgh}<h4>{esc(co)}</h4><p class="kind">{esc(kind)}</p><dl>'
            f'<dt>Задача</dt><dd>{esc(task)}</dd><dt>Решение</dt><dd>{esc(sol)}</dd>'
            f'<dt>Результат</dt><dd>{esc(res)}</dd></dl><p class="nom{win}">{esc(nom)}</p></article>')

def criteria_md():
    out = []
    for i, n in enumerate(NOMS, 1):
        out.append(f'### 5.{i}. Категория «{n["title"]}»\n\n{n["desc"]}\n\nКритерии оценки номинации:\n')
        out += [f'- **{a}.** {b}' for a, b in n['crit']]
        out.append('')
    return '\n'.join(out)

def md_inline(t):
    return markdown.markdown(t, extensions=['sane_lists'])

def block_item(kind, body, mod):
    lines = body.strip('\n').split('\n'); top = ''
    if lines and lines[0].startswith('!icon '):
        top = f'<img class="ic" src="{esc(lines[0][6:].strip())}" alt="" loading="lazy">'; lines = lines[1:]
    elif lines and lines[0].startswith('!person '):
        name, role = [x.strip() for x in lines[0][8:].split('|')]
        initials = ''.join(w[0] for w in name.split()[:2])
        top = f'<div class="who"><span class="av">{esc(initials)}</span><div><b>{esc(name)}</b><small>{esc(role)}</small></div></div>'; lines = lines[1:]
    elif lines and lines[0].startswith('!juror '):   # advice card: text first, signed below with a round photo
        src, name, role = [x.strip() for x in lines[0][7:].split('|')]; lines = lines[1:]
        lines = lines + ['', f'!sign {src} | {name} | {role}']
    elif lines and lines[0].startswith('!photo '):
        src, name, role = [x.strip() for x in lines[0][7:].split('|')]
        top = f'<div class="who"><img class="av" src="{esc(src)}" alt="{esc(name)}" loading="lazy"><div><b>{esc(name)}</b><small>{esc(role)}</small></div></div>'; lines = lines[1:]
    def sign(m): return (f'<div class="sign"><img src="{esc(m[1])}" alt="{esc(m[2])}" loading="lazy">'
                         f'<p><b>{esc(m[2])}</b><small>{esc(m[3])}</small></p></div>')
    # "!sign photo | name | role" anywhere in a card → signature with a round photo
    inner = md_inline(re.sub(r'^!sign (.+?) \| (.+?) \| (.+)$', sign, '\n'.join(lines), flags=re.M))
    if kind == 'split': return f'<div class="card{" " + mod if mod else ""}">{inner}</div>'
    if kind == 'quote': return f'<figure class="card"><blockquote>{inner}</blockquote><figcaption>{top}</figcaption></figure>'
    tag = {'dodont': ('Не стоит' if mod == 'dont' else 'Приветствуется')}.get(kind, '')
    badge = f'<span class="badge">{tag}</span>' if tag else ''
    return f'<div class="card{" " + mod if mod else ""}">{badge}{top}{inner}</div>'

def blocks(text):
    out, i, L = [], 0, text.split('\n')
    while i < len(L):
        ln = L[i]
        if ln.startswith(':::') and len(ln) > 3:
            kind = ln[3:].strip(); i += 1; items, cur, mod = [], [], ''
            while i < len(L) and L[i].strip() != ':::':
                if L[i].startswith('+++'):
                    items.append((cur, mod)); cur, mod = [], L[i][3:].strip()
                else: cur.append(L[i])
                i += 1
            items.append((cur, mod)); i += 1
            out.append(f'<div class="blk blk-{kind}">' + ''.join(block_item(kind, '\n'.join(c), m) for c, m in items) + '</div>')
            continue
        out.append(ln); i += 1
    return '\n'.join(out)

def render_md(text):
    """Returns (h1, lead_html, meta_html, body_html)."""
    text = text.replace('[[CRITERIA]]', criteria_md())
    text = blocks(text)
    lines, out, buf = text.split('\n'), [], []
    def flush():
        if buf: out.append('<div class="cases">' + ''.join(buf) + '</div>'); buf.clear()
    for ln in lines:
        if ln.startswith('C: '):
            buf.append(case_html(ln)); continue
        flush()
        m = re.match(r'\[\[CTA (.+?) \| (.+?) \| (.+?)\]\]', ln)
        if m:
            out.append(f'<div class="cta"><p>{esc(m[1])}</p><a class="btn" href="{esc(m[3])}"><span>{esc(m[2])}</span></a></div>')
            continue
        out.append(ln)
    flush()
    text = '\n'.join(out)
    h1 = re.search(r'^# (.+)$', text, re.M)[1]
    text = re.sub(r'^# .+\n', '', text, count=1, flags=re.M)
    meta = ''
    cover = ''
    m = re.search(r'^\[\[COVER (.+?)\]\]$', text, re.M)
    if m:
        cover = m[1]; text = text.replace(m[0], '')
    m = re.search(r'^\[\[META (.+?)\]\]$', text, re.M)
    if m:
        meta = '<div class="meta-row">' + ''.join(f'<span>{esc(x.strip())}</span>' for x in m[1].split('|')) + '</div>'
        text = text.replace(m[0], '')
    # first paragraph (before any heading/toc) becomes the lead
    lead = ''
    m = re.match(r'\s*([^\n#\[>].*?)\n\n', text, re.S)
    if m and not m[1].startswith(('-', '1.', '<', '[[')):
        lead = m[1].strip()
        text = text[m.end():]
    text = text.replace('[[TOC]]', '[TOC]')
    md = markdown.Markdown(extensions=['tables', 'toc', 'sane_lists'],
                           extension_configs={'toc': {'slugify': slugify_unicode, 'toc_depth': '2-3', 'title': 'Содержание'}})
    body = md.convert(text)
    body = body.replace('<div class="toc"><span class="toctitle">Содержание</span>', '<nav class="toc" aria-label="Содержание"><p>Содержание</p>')
    if '<nav class="toc"' in body:
        body = re.sub(r'(<nav class="toc".*?</ul>\s*)</div>', r'\1</nav>', body, count=1, flags=re.S)
    lead_html = markdown.markdown(lead)[3:-4] if lead else ''
    return h1, lead_html, meta, body, cover

def article(fname, src, title, desc, crumb, active='', h1cls='', side_toc=False):
    h1, lead, meta, body, cover = render_md((DATA / src).read_text(encoding='utf-8'))
    lead_block = f'<p class="lead">{lead}</p>' if lead else ''
    if side_toc:   # two columns: the article on the left, its table of contents in a sticky column on the right
        m = re.search(r'<nav class="toc".*?</nav>', body, re.S)
        toc = m[0] if m else ''; body = body.replace(toc, '')
        b = f'''<section class="phead has-cover"><div class="wrap"><div class="ph-grid"><div>{crumbs((crumb, None))}<h1 class="{h1cls}">{esc(h1)}</h1>{lead_block}{meta}</div><img class="cover" src="{esc(cover)}" alt=""></div></div></section>
<main><div class="wrap art-grid"><article class="prose">{body}</article><aside class="art-side">{toc}</aside></div></main>'''
        return page(fname, title, desc, b, active)
    if cover:
        b = f'''<section class="phead has-cover"><div class="wrap"><div class="ph-grid"><div>{crumbs((crumb, None))}<h1 class="{h1cls}">{esc(h1)}</h1>{lead_block}{meta}</div><img class="cover" src="{esc(cover)}" alt=""></div></div></section>
<main><div class="wrap narrow wide-ok"><article class="prose">{body}</article></div></main>'''
        return page(fname, title, desc, b, active)
    b = f'''<section class="phead"><div class="wrap narrow">{crumbs((crumb, None))}<h1 class="{h1cls}">{esc(h1)}</h1>{lead_block}{meta}</div></section>
<main><div class="wrap narrow"><article class="prose">{body}</article></div></main>'''
    return page(fname, title, desc, b, active)

# ---------- winners ----------
def winners(fname, src, year, active):
    txt = (DATA / src).read_text(encoding='utf-8').split('\n')
    h1 = txt[0][2:]; desc = txt[1][2:]
    blocks, cur = [], None
    for ln in txt[2:]:
        if ln.startswith('## '): cur = {'t': ln[3:], 'w': [], 'f': []}; blocks.append(cur)
        elif ln.startswith('W: '): cur['w'].append([x.strip() for x in ln[3:].split('|')])
        elif ln.startswith('F: '): cur['f'].append([x.strip() for x in ln[3:].split('|')])
    jump, secs = [], []
    for i, bl in enumerate(blocks, 1):
        sid = f'n{i}'
        jump.append(f'<a href="#{sid}">{esc(bl["t"])}</a>')
        def wcard(lg, c, p):
            logo = f'<img src="{logo_url(lg)}" alt="{esc(c)}" loading="lazy">' if lg != '-' else f'<span class="nologo">{esc(c)}</span>'
            return f'<div class="winner"><div class="wlogo">{logo}</div><div><span class="tag">Победитель</span><h3>{esc(c)}</h3><p>{esc(p)}</p></div></div>'
        w = ''.join(wcard(*x) for x in bl['w'])
        f = ''
        if bl['f']:
            cards = []
            for logo, c, p in bl['f']:
                lg = f'<img src="{logo_url(logo)}" alt="{esc(c)}" loading="lazy">' if logo != '-' else f'<span>{esc(c[:1])}</span>'
                cards.append(f'<div class="fin"><div class="lg">{lg}</div><b>{esc(c)}</b><p>{esc(p)}</p></div>')
            f = '<p class="finals-label">Финалисты</p><div class="finals">' + ''.join(cards) + '</div>'
        secs.append(f'<section class="nomblock" id="{sid}"><h2>{esc(bl["t"])}</h2><div>{w}{f}</div></section>')
    other = 2025 if year == 2026 else 2026
    switch = (f'<div class="year-switch" aria-label="Год">'
              f'<a href="shortlist-2026.html"{" aria-current=page" if year == 2026 else ""}>2026</a>'
              f'<a href="shortlist-2025.html"{" aria-current=page" if year == 2025 else ""}>2025</a></div>')
    b = f'''<section class="phead"><div class="wrap">{crumbs((f"Лауреаты {year}", None))}<h1 class="long">{esc(h1)}</h1><p class="lead">{esc(desc)}</p>{switch}</div></section>
<main><div class="wrap"><nav class="nom-jump" aria-label="Номинации">{''.join(jump)}</nav>{''.join(secs)}</div></main>'''
    return page(fname, f'Шорт-лист премии Generation AI {year}', desc, b, active)

# ---------- jury ----------
JURY_PH = {name: f'assets/jury/{slug}.webp' for name, slug in [
 ('AION', 'aion'), ('Андрей Рыбинцев', 'rybintsev'), ('Максим Волошин', 'voloshin'), ('Юлия Пивоварова', 'pivovarova'),
 ('Михаил Неверов', 'neverov'), ('Константин Паршин', 'parshin'), ('Владимир Сидоров', 'sidorov'), ('Валерий Кардашов', 'kardashov'),
 ('Дмитрий Мацера', 'matsera'), ('Наталья Балыбердина', 'balyberdina'), ('Артур Самигуллин', 'samigullin'), ('Дмитрий Васильев', 'vasiliev'),
 ('Роман Куцев', 'kutsev'), ('Павел Новиков', 'novikov'), ('Юрий Денисов', 'denisov'), ('Аркадий Сандлер', 'sandler'),
 ('Денис Кузнецов', 'kuznetsov'), ('Дмитрий Шевелев', 'shevelev'), ('Алексей Жабин', 'zhabin'), ('Вячеслав Тарасов', 'tarasov')]}
def jury():
    txt = (DATA / 'jury.txt').read_text(encoding='utf-8').split('\n')
    cards = []
    for ln in txt:
        if not ln.startswith('J: '): continue
        name, role = [x.strip() for x in ln[3:].split('|')]
        ph = JURY_PH.get(name)
        initials = ''.join(w[0] for w in name.split()[:2])
        inner = f'<img src="{ph}" alt="{esc(name)}" loading="lazy">' if ph else f'<span class="mono">{esc(initials)}</span>'
        if name == 'AION' and not ph: inner = '<span class="mono ai">AI</span>'
        cards.append(f'<div class="jc"><div class="ph">{inner}</div><h3>{esc(name)}</h3><p>{esc(role)}</p></div>')
    b = f'''<section class="phead"><div class="wrap">{crumbs(("Жюри", None))}<h1>{esc(txt[0][2:])}</h1><p class="lead">{esc(txt[1][2:])}</p></div></section>
<main><div class="wrap"><div class="jgrid">{''.join(cards)}</div></div></main>'''
    return page('jury.html', 'Жюри', txt[1][2:], b)

# ---------- galleries ----------
# ceremony video shown at the top of each gallery page
GAL_VIDEO = {2026: 'https://just-ai.com/video/GEN_AI_AWARDS_26_1.mp4', 2025: 'https://just-ai.com/video/LOFT_HALL_50.mp4'}

def gallery(year, imgs, active):
    vid = GAL_VIDEO.get(year)
    video = f'<div class="gvid"><video src="{vid}" controls playsinline preload="metadata"></video></div>' if vid else ''
    if imgs:
        shots = ''.join(f'<button data-full="{src}" aria-label="Открыть фото {i}"><img src="{src}" alt="Generation AI Awards {year}, фото {i}" loading="lazy"></button>'
                        for i, src in enumerate(imgs, 1))
        content = f'<div class="ggrid">{shots}</div><div class="lb" id="lb" role="dialog" aria-label="Просмотр фото"><img alt=""><button class="x" aria-label="Закрыть">×</button><button class="p" aria-label="Предыдущее">←</button><button class="n" aria-label="Следующее">→</button></div>'
    else:
        content = ('<div class="empty"><b>Фотографии 2025 года пока не добавлены</b>'
                   '<p>Положите снимки в папку <code>images/gallery-2025/</code> и перечислите их в <code>data/gallery_2025.txt</code>, затем пересоберите сайт.</p>'
                   '<a class="btn ghost" href="gallery-2026.html"><span>Смотреть галерею 2026</span></a></div>')
    b = f'''<section class="phead"><div class="wrap">{crumbs((f"Галерея {year} год", None))}<h1>{year} год</h1><p class="lead">Самые яркие моменты премии Generation AI Awards {year}</p></div></section>
<main><div class="wrap">{video}{content}</div></main>'''
    return page(f'gallery-{year}.html', f'Галерея {year} год', f'Самые яркие моменты Премии Generation AI Awards {year}', b, active)

# ---------- nominations ----------
def other_noms(skip):
    links = ''.join(f'<a href="{nom_file(s)}">{esc(NOM_TITLE[s])}</a>' for s in NOM_ORDER if s != skip)
    return f'<section class="other-noms"><h2>Другие номинации</h2><div class="onl">{links}</div></section>'

def nomination(n):
    crit = ''.join(f'<div class="ccard"><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for a, b in n['crit'])
    lead = n.get('lead') or n['desc']
    apply = APPLY_BASE + n['slug']
    btn = f'<a class="btn" href="{apply}" target="_blank" rel="noopener"><span>Заполнить заявку</span></a>'
    b = f'''<section class="phead"><div class="wrap">{crumbs(("Номинации", "index.html#nom"), (n["title"], None))}<h1 class="long">Номинация «{esc(n["title"])}»</h1><p class="lead">{esc(lead)}</p><div class="ph-cta">{btn}</div></div></section>
<main><div class="wrap"><div class="crit">
  <h2>Критерии оценки номинации</h2><div class="cgrid">{crit}</div>
  <div class="crit-foot">
    <div class="apply-row"><p>Готовы участвовать? Заявка подается бесплатно, до 3 проектов от одной компании.</p>{btn}</div>
    <div class="help"><p>Не знаете, какую номинацию выбрать или как оформить заявку? Читайте бриф с советами членов жюри <a href="ai-navigator.html">AI-Навигатор 2.0</a> и <a href="protocol.html">Положение премии</a>.</p></div>
  </div>
</div>{other_noms(n["slug"])}</div></main>'''
    return page(nom_file(n['slug']), f'Номинация «{n["title"]}» премии Generation AI Awards', lead, b, 'nom', 'nom-page')

def special(slug, src, title, desc):
    h1, lead, meta, body, cover = render_md((DATA / src).read_text(encoding='utf-8'))
    lead_block = f'<p class="lead">{lead}</p>' if lead else ''
    b = f'''<section class="phead"><div class="wrap narrow">{crumbs(("Номинации", "index.html#nom"), (NOM_TITLE[slug], None))}<h1 class="long">{esc(h1)}</h1>{lead_block}</div></section>
<main><div class="wrap narrow"><article class="prose">{body}</article></div><div class="wrap">{other_noms(slug)}</div></main>'''
    return page(nom_file(slug), title, desc, b, 'nom', f'nom-page nom-text nom-{slug}')

if __name__ == '__main__':
    made = []
    made.append(winners('shortlist-2026.html', 'shortlist_2026.txt', 2026, 'w26'))
    made.append(winners('shortlist-2025.html', 'shortlist_2025.txt', 2025, 'w25'))
    made.append(jury())
    # gallery lists hold local paths (images/gallery-<year>/*.webp), one per line
    g26 = ['statuettes-2026.jpg'] + (DATA / 'gal2026.txt').read_text().split()
    made.append(gallery(2026, g26, 'g26'))
    g25 = [l for l in (DATA / 'gallery_2025.txt').read_text().split()] if (DATA / 'gallery_2025.txt').exists() else []
    made.append(gallery(2025, g25, 'g25'))
    made.append(article('ai-navigator.html', 'ai_navigator.md', 'AI-Навигатор 2.0',
                        'Пошаговое руководство для оформления заявок для премии Generation AI Awards', 'AI-Навигатор 2.0', 'nav', side_toc=True))
    made.append(article('analytical-review.html', 'analytical_review.md',
                        'От чат-бота к агенту: как генеративный AI изменил рынок в 2026 | Generation AI Awards',
                        'Аналитика по 200+ проектам премии: тренды по отраслям, живые кейсы с цифрами и главный вывод — бизнес научился применять AI избирательно.',
                        'Аналитический обзор', 'rev', side_toc=True))
    made.append(article('protocol.html', 'protocol.md', 'Положение о премии Generation AI Awards',
                        'Правила участия, номинации и критерии оценки премии Generation AI Awards', 'Положение премии', h1cls='long'))
    for n in NOMS:
        if not n.get('protocol_only'): made.append(nomination(n))
    made.append(special('choice', 'choice.md', 'Номинация «Выбор генеративного AI» премии Generation AI Awards',
                        'AI-эксперт AION оценит все проекты участников премии и определит абсолютного победителя.'))
    made.append(special('ink', 'ink.md', 'Спецприз от медиа для предпринимателей «Инк»',
                        'Спецприз от редакции «Инк» за проект с осмысленным предпринимательским подходом к генеративному AI.'))
    print(len(made), 'pages:', ', '.join(made))
