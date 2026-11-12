import json
import os
import re
import csv
import io
import random
import time
import threading
import queue
import streamlit as st
from datetime import datetime
from playwright.sync_api import sync_playwright

# ══════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FB Scraper Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
#  GLOBAL CSS — PREMIUM GLASSMORPHISM DARK UI
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #050810 !important;
}

/* ── Animated background mesh ── */
.main > .block-container {
    background: transparent !important;
    padding-top: 1.5rem !important;
    max-width: 1400px !important;
}
.main::before {
    content: '';
    position: fixed; inset: 0; z-index: -1;
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(56,139,253,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(139,92,246,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 50% 60% at 50% 50%, rgba(5,8,16,1) 0%, #050810 100%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #0d1326 50%, #0a0f1e 100%) !important;
    border-right: 1px solid rgba(56,139,253,0.15) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem !important; }
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

/* ── Sidebar section labels ── */
.sidebar-section {
    font-size: 10px; font-weight: 700; letter-spacing: 2px;
    color: #388bfd !important; text-transform: uppercase;
    margin: 1.4rem 0 0.5rem; padding-bottom: 4px;
    border-bottom: 1px solid rgba(56,139,253,0.2);
}

/* ── Category pills ── */
.cat-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 0.5rem 0;
}
.cat-pill {
    background: rgba(22,27,34,0.8);
    border: 1px solid rgba(56,139,253,0.2);
    border-radius: 10px; padding: 10px 8px;
    text-align: center; cursor: pointer;
    transition: all 0.2s ease; font-size: 12px; font-weight: 500;
}
.cat-pill:hover { border-color: #388bfd; background: rgba(56,139,253,0.1); }
.cat-pill.active {
    border-color: #388bfd;
    background: linear-gradient(135deg, rgba(56,139,253,0.2), rgba(56,139,253,0.05));
    color: #58a6ff !important;
}

/* ── Main header ── */
.app-header {
    display: flex; align-items: center; gap: 16px;
    margin-bottom: 0.5rem;
}
.app-logo {
    width: 52px; height: 52px; border-radius: 14px;
    background: linear-gradient(135deg, #1f6feb, #388bfd, #7c3aed);
    display: flex; align-items: center; justify-content: center;
    font-size: 26px; box-shadow: 0 0 24px rgba(56,139,253,0.4);
}
.app-title { font-size: 28px; font-weight: 800; letter-spacing: -0.5px; }
.app-title span { background: linear-gradient(90deg, #58a6ff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.app-sub { font-size: 13px; color: #484f58 !important; margin-top: 2px; }

/* ── Divider ── */
.glow-divider {
    height: 1px; border: none; margin: 1.2rem 0;
    background: linear-gradient(90deg, transparent, rgba(56,139,253,0.4), transparent);
}

/* ── Stat cards ── */
.stats-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin: 1.2rem 0; }
.stat-card {
    background: rgba(22,27,34,0.7);
    border: 1px solid rgba(48,54,61,0.8);
    border-radius: 14px; padding: 18px 14px; text-align: center;
    backdrop-filter: blur(10px);
    transition: border-color 0.3s, transform 0.2s;
    position: relative; overflow: hidden;
}
.stat-card::before {
    content: ''; position: absolute; inset: 0; border-radius: 14px;
    background: linear-gradient(135deg, rgba(56,139,253,0.04), transparent);
}
.stat-card:hover { border-color: rgba(56,139,253,0.5); transform: translateY(-2px); }
.stat-num {
    font-size: 30px; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(135deg, #58a6ff, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-lbl { font-size: 11px; color: #484f58; font-weight: 500; letter-spacing: 0.5px; margin-top: 4px; }
.stat-icon { font-size: 20px; margin-bottom: 6px; }

/* ── Live log ── */
.log-panel {
    background: rgba(13,17,23,0.95);
    border: 1px solid rgba(48,54,61,0.8);
    border-radius: 14px; padding: 16px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; line-height: 1.8;
    max-height: 300px; overflow-y: auto;
    backdrop-filter: blur(8px);
}
.log-line-ok    { color: #3fb950; }
.log-line-info  { color: #58a6ff; }
.log-line-warn  { color: #d29922; }
.log-line-error { color: #f85149; }
.log-line-done  { color: #a78bfa; font-weight: 600; }

/* ── Post cards ── */
.post-card {
    background: rgba(22,27,34,0.75);
    border: 1px solid rgba(48,54,61,0.9);
    border-radius: 16px; padding: 0; margin-bottom: 20px;
    backdrop-filter: blur(12px);
    transition: border-color 0.3s, box-shadow 0.3s;
    overflow: hidden;
}
.post-card:hover {
    border-color: rgba(56,139,253,0.5);
    box-shadow: 0 8px 32px rgba(56,139,253,0.12);
}
.card-header {
    display: flex; justify-content: space-between; align-items: flex-start;
    padding: 18px 20px 14px; border-bottom: 1px solid rgba(48,54,61,0.6);
    gap: 12px;
}
.author-block { display: flex; align-items: center; gap: 12px; }
.author-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, #1f6feb, #7c3aed);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700; color: white !important;
    flex-shrink: 0;
}
.author-name { font-size: 14px; font-weight: 600; color: #f0f6fc !important; }
.author-time { font-size: 11px; color: #484f58; margin-top: 2px; }
.post-num-badge {
    background: linear-gradient(90deg, #1f6feb, #7c3aed);
    color: white !important; font-size: 11px; font-weight: 700;
    padding: 3px 12px; border-radius: 20px; white-space: nowrap;
    flex-shrink: 0;
}
.card-body { padding: 16px 20px; }
.post-text {
    font-size: 14px; line-height: 1.75; color: #c9d1d9;
    margin-bottom: 14px; white-space: pre-wrap; word-break: break-word;
}
.post-url-link {
    font-size: 11px; color: #388bfd !important;
    word-break: break-all; margin-bottom: 10px; display: block;
}

/* ── Reaction badges ── */
.reactions-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
.reaction-badge {
    background: rgba(13,17,23,0.8);
    border: 1px solid rgba(48,54,61,0.8);
    border-radius: 20px; padding: 4px 12px;
    font-size: 12px; color: #8b949e;
    display: flex; align-items: center; gap: 5px;
}
.reaction-badge .r-num { color: #f0f6fc; font-weight: 600; }

/* ── Image grid ── */
.section-head {
    font-size: 11px; font-weight: 700; letter-spacing: 1.5px;
    color: #388bfd; text-transform: uppercase; margin: 16px 0 8px;
    display: flex; align-items: center; gap: 6px;
}
.img-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 8px; margin-bottom: 14px;
}
.img-thumb {
    border-radius: 10px; overflow: hidden; aspect-ratio: 1;
    background: rgba(13,17,23,0.5); border: 1px solid rgba(48,54,61,0.6);
}
.img-thumb img { width: 100%; height: 100%; object-fit: cover; }
.img-url-tag {
    font-size: 10px; color: #388bfd;
    word-break: break-all; padding: 2px 0;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Comments ── */
.comment-block {
    background: rgba(13,17,23,0.6);
    border-left: 3px solid rgba(56,139,253,0.4);
    border-radius: 0 10px 10px 0;
    padding: 10px 14px; margin: 6px 0;
}
.comment-author {
    font-size: 12px; font-weight: 600; color: #58a6ff;
    margin-bottom: 3px;
}
.comment-text { font-size: 13px; color: #8b949e; line-height: 1.6; }

/* ── Card footer ── */
.card-footer {
    padding: 10px 20px 14px;
    display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
}
.meta-chip {
    background: rgba(13,17,23,0.6);
    border: 1px solid rgba(48,54,61,0.6);
    border-radius: 8px; padding: 3px 10px;
    font-size: 11px; color: #484f58;
}
.meta-chip span { color: #8b949e; font-weight: 500; }

/* ── Category tabs ── */
.cat-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin: 0.8rem 0 1.2rem; }
.cat-tab {
    padding: 8px 18px; border-radius: 10px; font-size: 13px; font-weight: 600;
    border: 1px solid rgba(48,54,61,0.8); cursor: pointer;
    background: rgba(22,27,34,0.7); color: #8b949e;
    transition: all 0.2s;
}
.cat-tab:hover { border-color: #388bfd; color: #58a6ff; }
.cat-tab.active {
    background: linear-gradient(135deg, rgba(31,111,235,0.25), rgba(124,58,237,0.15));
    border-color: #388bfd; color: #58a6ff;
    box-shadow: 0 0 12px rgba(56,139,253,0.2);
}

/* ── Streamlit widget overrides ── */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    background: rgba(13,17,23,0.9) !important;
    border: 1px solid rgba(48,54,61,0.8) !important;
    border-radius: 8px !important; color: #c9d1d9 !important;
    font-size: 13px !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #388bfd !important;
    box-shadow: 0 0 0 2px rgba(56,139,253,0.2) !important;
}
.stFileUploader {
    background: rgba(13,17,23,0.6) !important;
    border: 1px dashed rgba(56,139,253,0.3) !important;
    border-radius: 10px !important;
}
.stCheckbox { color: #c9d1d9 !important; }
.stCheckbox > label > div { background: rgba(56,139,253,0.15) !important; }

/* Start button */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1f6feb, #388bfd, #7c3aed) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-size: 14px !important; padding: 0.65rem 1.6rem !important;
    width: 100%; letter-spacing: 0.3px;
    box-shadow: 0 4px 20px rgba(56,139,253,0.35) !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important; transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

/* Download button */
div[data-testid="stDownloadButton"] > button {
    background: rgba(22,27,34,0.9) !important;
    border: 1px solid rgba(56,139,253,0.4) !important;
    color: #58a6ff !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 13px !important;
}

/* Toggle/checkbox accent */
.stCheckbox span { color: #c9d1d9 !important; }
[data-testid="stMarkdownContainer"] p { color: #8b949e; font-size: 13px; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(56,139,253,0.3); border-radius: 10px; }

/* Empty state */
.empty-state {
    text-align: center; padding: 80px 20px;
    border: 1px dashed rgba(48,54,61,0.8);
    border-radius: 16px; background: rgba(22,27,34,0.4);
}
.empty-icon { font-size: 64px; margin-bottom: 16px; }
.empty-title { font-size: 22px; font-weight: 700; color: #484f58; }
.empty-sub { font-size: 14px; color: #30363d; margin-top: 8px; }

/* Progress pulse */
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
.scraping-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(56,139,253,0.1); border: 1px solid rgba(56,139,253,0.3);
    border-radius: 20px; padding: 6px 16px; margin-bottom: 12px;
    font-size: 13px; font-weight: 600; color: #58a6ff;
}
.pulse-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #388bfd; animation: pulse 1.2s infinite;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════
CATEGORIES = {
    "posts":   {"label": "Posts",    "icon": "📝", "url": "https://www.facebook.com/search/posts/?q={q}"},
    "groups":  {"label": "Groups",   "icon": "👥", "url": "https://www.facebook.com/search/groups/?q={q}"},
    "pages":   {"label": "Pages",    "icon": "📄", "url": "https://www.facebook.com/search/pages/?q={q}"},
    "people":  {"label": "People",   "icon": "👤", "url": "https://www.facebook.com/search/people/?q={q}"},
    "events":  {"label": "Events",   "icon": "📅", "url": "https://www.facebook.com/search/events/?q={q}"},
    "videos":  {"label": "Videos",   "icon": "🎥", "url": "https://www.facebook.com/search/videos/?q={q}"},
    "reels":   {"label": "Reels",    "icon": "🎞️", "url": "https://www.facebook.com/search/reels/?q={q}"},
    "marketplace": {"label": "Market", "icon": "🛒", "url": "https://www.facebook.com/search/marketplace/?q={q}"},
}


def human_delay(a=2.0, b=5.0):
    time.sleep(random.uniform(a, b))


def smooth_scroll(page, steps=3, dist=400):
    for _ in range(steps):
        try:
            page.mouse.wheel(0, dist)
            time.sleep(random.uniform(0.4, 0.9))
        except Exception:
            break


def sanitize_cookie(c):
    clean = c.copy()
    s = clean.get("sameSite")
    clean["sameSite"] = "None" if s in ("no_restriction", None) else str(s).capitalize()
    for k in ("storeId", "hostOnly", "session"):
        clean.pop(k, None)
    return clean


def safe_text(elem, timeout=400):
    try:
        return elem.inner_text(timeout=timeout).strip()
    except Exception:
        return ""


def extract_images(post_elem, min_width=120):
    """Grab real image URLs — skip icons, SVGs, and data-URIs."""
    imgs = []
    # Patterns that identify UI/icon images to discard
    SKIP_PATTERNS = (
        "data:",        # inline SVG/base64 icons
        "emoji",        # emoji sprites
        "rsrc.php",     # Facebook static resources
        "/static/",     # static assets
        "1x1",          # tracking pixels
        ".gif",         # animated GIFs (often spinners)
    )
    try:
        img_els = post_elem.locator("img").all()
        for img in img_els:
            src = img.get_attribute("src") or ""
            if not src:
                continue
            # Discard known non-content images
            if any(p in src for p in SKIP_PATTERNS):
                continue
            # Only keep CDN-hosted Facebook content images
            if not ("fbcdn.net" in src or "fbsbx.com" in src or "cdninstagram.com" in src):
                continue
            imgs.append(src)
    except Exception:
        pass
    return list(dict.fromkeys(imgs))[:8]  # deduplicate, max 8


def extract_reactions(post_elem):
    """Try to get reactions/like count text."""
    reactions = {"total": "0", "likes": "", "comments": "", "shares": ""}
    try:
        # Reaction total
        r_spans = post_elem.locator("[aria-label*='reaction'], [aria-label*='people reacted']").all()
        for s in r_spans:
            lbl = s.get_attribute("aria-label") or ""
            num = re.search(r"[\d,]+", lbl)
            if num:
                reactions["total"] = num.group(0)
                break
        # Comments count
        c_btns = post_elem.locator("[aria-label*='comment']").all()
        for b in c_btns:
            lbl = b.get_attribute("aria-label") or ""
            num = re.search(r"[\d,]+", lbl)
            if num:
                reactions["comments"] = num.group(0)
                break
        # Shares count
        s_btns = post_elem.locator("[aria-label*='share']").all()
        for b in s_btns:
            lbl = b.get_attribute("aria-label") or ""
            num = re.search(r"[\d,]+", lbl)
            if num:
                reactions["shares"] = num.group(0)
                break
    except Exception:
        pass
    return reactions


def extract_author(post_elem):
    try:
        # Strong tag usually holds author name
        strong = post_elem.locator("strong").first
        name = safe_text(strong)
        if name:
            return name
    except Exception:
        pass
    return "Unknown"


def extract_post_url(post_elem):
    try:
        links = post_elem.locator("a[href*='/posts/'], a[href*='/permalink/'], a[href*='story_fbid']").all()
        for link in links:
            href = link.get_attribute("href") or ""
            if href:
                return href.split("?")[0]
    except Exception:
        pass
    return ""


def extract_timestamp(post_elem):
    try:
        abbr = post_elem.locator("abbr[data-utime]").first
        ts = abbr.get_attribute("title") or abbr.get_attribute("data-utime") or ""
        return ts
    except Exception:
        pass
    return ""


def extract_comments_rich(post_elem, main_text):
    """Return list of {author, text} dicts from visible comments."""
    comments = []
    try:
        articles = post_elem.locator("div[role='article']").all()
        for art in articles:
            # Each article: first strong = author, rest = text
            author = "Unknown"
            try:
                s = art.locator("strong").first
                author = safe_text(s) or "Unknown"
            except Exception:
                pass
            text = safe_text(art)
            if text and text.strip() != main_text.strip():
                # Remove the author from the start of text if duplicated
                body = text
                if body.startswith(author):
                    body = body[len(author):].strip(" ·\n:")
                if body:
                    comments.append({"author": author, "text": body[:500]})
    except Exception:
        pass
    return comments[:15]


# ══════════════════════════════════════════════════════════
#  SCRAPER CORE — Posts
# ══════════════════════════════════════════════════════════
def scrape_posts(cookies, query, max_items, scrape_images, scrape_comments, log_q):
    dataset = []

    def log(msg, level="info"):
        log_q.put((msg, level))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=60)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            java_script_enabled=True,
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        url = f"https://www.facebook.com/search/posts/?q={query}"
        log(f"Navigating → {url}", "info")
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)

        log("Waiting for feed…", "info")
        try:
            page.wait_for_selector("div[role='feed']", timeout=18_000)
        except Exception:
            log("Feed not found — check cookies / login.", "warn")

        human_delay(3.0, 5.5)
        log("Scrolling feed…", "info")
        smooth_scroll(page, steps=5, dist=400)
        human_delay(2.0, 3.5)

        containers = page.locator("div[role='feed'] > div").all()
        log(f"Found {len(containers)} candidate containers", "info")

        count = 0
        for elem in containers:
            if count >= max_items:
                break

            # Expand "See more"
            try:
                btn = elem.locator("div[role='button']:has-text('See more')").first
                if btn.is_visible(timeout=500):
                    btn.click(); human_delay(0.6, 1.2)
            except Exception:
                pass

            # Get text
            blocks = elem.locator("div[dir='auto']").all()
            parts = [safe_text(b) for b in blocks if len(safe_text(b)) > 20]
            if not parts:
                continue
            main_text = parts[0]

            # Author / meta
            author  = extract_author(elem)
            ts      = extract_timestamp(elem)
            post_url = extract_post_url(elem)
            reactions = extract_reactions(elem)

            # Images
            images = []
            if scrape_images:
                images = extract_images(elem)
                if images:
                    log(f"  [{count+1}] Found {len(images)} image(s)", "ok")

            # Comments
            comments = []
            if scrape_comments:
                try:
                    cb = elem.locator(
                        "div[role='button']:has-text('comment'), div[role='button']:has-text('Comment')"
                    ).first
                    if cb.is_visible(timeout=500):
                        cb.click(); human_delay(1.2, 2.2)
                except Exception:
                    pass
                comments = extract_comments_rich(elem, main_text)

            record = {
                "id": count + 1,
                "scraped_at": datetime.now().isoformat(timespec="seconds"),
                "category": "post",
                "author": author,
                "timestamp": ts or "N/A",
                "post_url": post_url,
                "content": main_text,
                "word_count": len(main_text.split()),
                "char_count": len(main_text),
                "reactions": reactions,
                "images": images,
                "comments_count": len(comments),
                "comments": comments,
                "all_text_blocks": parts[:5],
            }
            dataset.append(record)
            count += 1

            log(
                f"Post #{count} scraped — {len(comments)} comments, "
                f"{len(images)} images, {reactions['total']} reactions",
                "ok",
            )
            human_delay(3.0, 6.0)
            smooth_scroll(page, steps=2, dist=300)

        log(f"Done — {len(dataset)} posts collected.", "done")
        human_delay(1.0, 2.0)
        browser.close()

    return dataset


# ══════════════════════════════════════════════════════════
#  SCRAPER CORE — Generic (Groups / Pages / People / Events / Videos / Reels)
# ══════════════════════════════════════════════════════════
def scrape_generic(cookies, query, category, max_items, scrape_images, log_q):
    dataset = []

    def log(msg, level="info"):
        log_q.put((msg, level))

    url_tpl = CATEGORIES[category]["url"]
    target_url = url_tpl.format(q=query)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=60)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        log(f"Navigating → {target_url}", "info")
        page.goto(target_url, wait_until="domcontentloaded", timeout=30_000)
        human_delay(3.5, 6.0)
        smooth_scroll(page, steps=4, dist=450)
        human_delay(2.0, 3.5)

        # Generic result cards differ per category — grab all substantial divs
        items = page.locator("div[role='article'], div[data-pagelet*='SearchResult'] > div, div[data-testid*='result']").all()
        # Fallback: all top-level feed children
        if len(items) < 2:
            items = page.locator("div[role='main'] > div > div").all()

        log(f"Found {len(items)} result containers", "info")
        count = 0

        for elem in items:
            if count >= max_items:
                break

            title = ""
            link  = ""
            desc  = ""
            images = []
            meta  = {}

            # Title — first heading or strong
            try:
                title = safe_text(elem.locator("h1, h2, h3, strong").first) or ""
            except Exception:
                pass

            if not title or len(title) < 3:
                # Try any dir=auto block
                try:
                    for b in elem.locator("div[dir='auto']").all():
                        t = safe_text(b)
                        if len(t) > 4:
                            title = t; break
                except Exception:
                    pass

            if not title:
                continue

            # Link
            try:
                link = elem.locator("a").first.get_attribute("href") or ""
                if link and not link.startswith("http"):
                    link = "https://www.facebook.com" + link
            except Exception:
                pass

            # Description / subtitle
            try:
                all_blocks = elem.locator("div[dir='auto']").all()
                desc_parts = [safe_text(b) for b in all_blocks if 5 < len(safe_text(b)) < 300 and safe_text(b) != title]
                desc = " | ".join(desc_parts[:3])
            except Exception:
                pass

            # Extra meta (members count, location, category text, etc.)
            try:
                spans = elem.locator("span").all()
                extras = [safe_text(s) for s in spans if 2 < len(safe_text(s)) < 80]
                meta["details"] = list(dict.fromkeys(extras))[:6]
            except Exception:
                pass

            # Images
            if scrape_images:
                images = extract_images(elem)

            record = {
                "id": count + 1,
                "scraped_at": datetime.now().isoformat(timespec="seconds"),
                "category": category,
                "title": title,
                "link": link,
                "description": desc,
                "meta": meta,
                "images": images,
            }
            dataset.append(record)
            count += 1
            log(f"{category.capitalize()} #{count} — {title[:60]}", "ok")
            human_delay(1.5, 3.0)

        log(f"Done — {len(dataset)} {category} items collected.", "done")
        browser.close()

    return dataset


# ══════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════
defaults = {
    "results": [],
    "logs": [],
    "running": False,
    "category": "posts",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px;">
        <div style="font-size:40px;">⚡</div>
        <div style="font-size:18px;font-weight:800;background:linear-gradient(90deg,#58a6ff,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            FB Scraper Pro
        </div>
        <div style="font-size:11px;color:#484f58;margin-top:4px;">Premium Extraction Tool</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">🔍 Search</div>', unsafe_allow_html=True)
    query = st.text_input("Query", value="artificial intelligence", label_visibility="collapsed",
                          placeholder="Enter search keyword…")

    st.markdown('<div class="sidebar-section">📂 Category</div>', unsafe_allow_html=True)
    # Render category grid with radio buttons mimicking pills
    cat_cols = st.columns(2)
    for i, (key, meta) in enumerate(CATEGORIES.items()):
        with cat_cols[i % 2]:
            is_active = st.session_state.category == key
            btn_label = f"{meta['icon']} {meta['label']}"
            if st.button(btn_label, key=f"cat_{key}",
                         help=f"Scrape {meta['label']}"):
                st.session_state.category = key
                st.rerun()

    st.markdown('<div class="sidebar-section">⚙️ Options</div>', unsafe_allow_html=True)
    max_items = st.number_input("Max items", min_value=1, max_value=100, value=5, step=1)
    scrape_images   = st.checkbox("📸 Scrape images",   value=True)
    scrape_comments = st.checkbox("💬 Scrape comments", value=True,
                                  disabled=(st.session_state.category != "posts"))

    st.markdown('<div class="sidebar-section">🍪 Cookies</div>', unsafe_allow_html=True)
    cookie_file = st.file_uploader("Upload cookies.json", type=["json"],
                                   label_visibility="collapsed")
    cookie_status = st.empty()
    cookies_loaded = []
    if cookie_file:
        try:
            raw = json.load(cookie_file)
            cookies_loaded = [sanitize_cookie(c) for c in raw]
            cookie_status.success(f"✓ {len(cookies_loaded)} cookies loaded")
        except Exception as e:
            cookie_status.error(f"Invalid JSON: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("⚡  Start Scraping", disabled=st.session_state.running)

    st.markdown("""
    <div style="margin-top:24px;padding:12px;background:rgba(248,81,73,0.07);
                border:1px solid rgba(248,81,73,0.2);border-radius:8px;font-size:11px;color:#8b949e;">
        ⚠️ For research/educational use only.<br>Respect Facebook's Terms of Service.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  MAIN HEADER
# ══════════════════════════════════════════════════════════
active_cat = CATEGORIES[st.session_state.category]
st.markdown(f"""
<div class="app-header">
    <div class="app-logo">{active_cat['icon']}</div>
    <div>
        <div class="app-title"><span>FB Scraper Pro</span></div>
        <div class="app-sub">
            Scraping <b style="color:#58a6ff">{active_cat['label']}</b>
            {"for <b style='color:#58a6ff'>\"" + query + "\"</b>" if query else ""}
            &nbsp;·&nbsp; {datetime.now().strftime("%d %b %Y, %H:%M")}
        </div>
    </div>
</div>
<hr class="glow-divider">
""", unsafe_allow_html=True)

# Category tab display (visual only)
tab_html = '<div class="cat-tabs">'
for key, meta in CATEGORIES.items():
    active_cls = "active" if key == st.session_state.category else ""
    tab_html += f'<span class="cat-tab {active_cls}">{meta["icon"]} {meta["label"]}</span>'
tab_html += "</div>"
st.markdown(tab_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  RUN SCRAPER
# ══════════════════════════════════════════════════════════
if run_btn:
    if not cookies_loaded:
        st.error("⚠️ Upload a cookies JSON file first.")
    elif not query.strip():
        st.error("⚠️ Enter a search query.")
    else:
        st.session_state.running = True
        st.session_state.results = []
        st.session_state.logs    = []

        log_q         = queue.Queue()
        result_holder = {}
        category      = st.session_state.category

        def _run():
            try:
                if category == "posts":
                    data = scrape_posts(
                        cookies_loaded, query.strip(), max_items,
                        scrape_images, scrape_comments, log_q
                    )
                else:
                    data = scrape_generic(
                        cookies_loaded, query.strip(), category,
                        max_items, scrape_images, log_q
                    )
                result_holder["data"] = data
            except Exception as exc:
                log_q.put((f"FATAL ERROR: {exc}", "error"))
                result_holder["data"] = []
            finally:
                log_q.put(("__DONE__", "done"))

        th = threading.Thread(target=_run, daemon=True)
        th.start()

        st.markdown('<div class="scraping-badge"><div class="pulse-dot"></div>Scraping in progress…</div>',
                    unsafe_allow_html=True)
        log_ph    = st.empty()
        log_lines = []
        level_cls = {"info": "log-line-info", "ok": "log-line-ok",
                     "warn": "log-line-warn", "error": "log-line-error", "done": "log-line-done"}

        while True:
            try:
                msg, lvl = log_q.get(timeout=1)
            except queue.Empty:
                continue
            if msg == "__DONE__":
                break
            cls = level_cls.get(lvl, "log-line-info")
            prefix = {"info": "›", "ok": "✓", "warn": "!", "error": "✗", "done": "★"}.get(lvl, "›")
            log_lines.append(f'<span class="{cls}">{prefix} {msg}</span>')
            log_ph.markdown(
                '<div class="log-panel">' + "<br>".join(log_lines) + "</div>",
                unsafe_allow_html=True,
            )

        th.join()
        st.session_state.results = result_holder.get("data", [])
        st.session_state.logs    = log_lines
        st.session_state.running = False

        if st.session_state.results:
            out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fb_scraped_data.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(st.session_state.results, f, ensure_ascii=False, indent=4)

        st.rerun()


# ══════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════
results  = st.session_state.results
logs     = st.session_state.logs
category = st.session_state.category

if results:
    # ── Stats row ──
    is_posts = category == "posts"
    total_comments = sum(r.get("comments_count", 0) for r in results) if is_posts else 0
    total_images   = sum(len(r.get("images", [])) for r in results)
    total_words    = sum(r.get("word_count", 0) for r in results) if is_posts else 0
    total_reactions = sum(
        int(r.get("reactions", {}).get("total", "0").replace(",", ""))
        for r in results if is_posts
    ) if is_posts else 0

    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-icon">{active_cat['icon']}</div>
            <div class="stat-num">{len(results)}</div>
            <div class="stat-lbl">Items Scraped</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">💬</div>
            <div class="stat-num">{total_comments}</div>
            <div class="stat-lbl">Comments</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📸</div>
            <div class="stat-num">{total_images}</div>
            <div class="stat-lbl">Images Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">👍</div>
            <div class="stat-num">{total_reactions:,}</div>
            <div class="stat-lbl">Total Reactions</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-num">{total_words:,}</div>
            <div class="stat-lbl">Total Words</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Download buttons ──
    json_bytes = json.dumps(results, ensure_ascii=False, indent=4).encode("utf-8")
    ts_str     = datetime.now().strftime("%Y%m%d_%H%M")

    # CSV export
    csv_buf = io.StringIO()
    if results:
        fieldnames = [k for k in results[0].keys() if k not in ("comments", "images", "meta", "reactions", "all_text_blocks")]
        writer = csv.DictWriter(csv_buf, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    dl1, dl2, _ = st.columns([1, 1, 3])
    with dl1:
        st.download_button("⬇️ Download JSON", data=json_bytes,
                           file_name=f"fb_{category}_{query[:20]}_{ts_str}.json",
                           mime="application/json")
    with dl2:
        st.download_button("⬇️ Download CSV", data=csv_buf.getvalue().encode("utf-8"),
                           file_name=f"fb_{category}_{query[:20]}_{ts_str}.csv",
                           mime="text/csv")

    st.markdown("<hr class='glow-divider'>", unsafe_allow_html=True)

    # ── Scrape log collapsible ──
    if logs:
        with st.expander("🖥️ Scrape Log", expanded=False):
            st.markdown('<div class="log-panel">' + "<br>".join(logs) + "</div>",
                        unsafe_allow_html=True)

    # ══ RENDER CARDS ══
    st.markdown(f"## {active_cat['icon']} {active_cat['label']} Results")

    for r in results:
        # ── POST card ──
        if category == "posts":
            author_init = (r.get("author") or "?")[0].upper()
            safe_content = r["content"].replace("<", "&lt;").replace(">", "&gt;")
            rx = r.get("reactions", {})
            imgs = r.get("images", [])
            comments = r.get("comments", [])

            # Images — rendered via st.image to avoid HTML escaping issues
            img_html = ""

            # Comments HTML
            cmts_html = ""
            if comments:
                cmts_html = f'<div class="section-head">💬 Comments ({len(comments)})</div>'
                for c in comments:
                    safe_auth = str(c.get("author", "")).replace("<", "&lt;").replace(">", "&gt;")
                    safe_body = str(c.get("text", "")).replace("<", "&lt;").replace(">", "&gt;")
                    cmts_html += (
                        '<div class="comment-block">'
                        f'<div class="comment-author">👤 {safe_auth}</div>'
                        f'<div class="comment-text">{safe_body}</div>'
                        '</div>'
                    )
            else:
                cmts_html = '<div style="font-size:12px;color:#30363d;padding:4px 0;">No comments captured</div>'

            post_url_html = ""
            if r.get("post_url"):
                pu = r["post_url"].replace('"', "").replace("'", "")
                post_url_html = f'<a class="post-url-link" href="{pu}" target="_blank">🔗 {pu}</a>'

            card = (
                '<div class="post-card">'
                '<div class="card-header">'
                '<div class="author-block">'
                f'<div class="author-avatar">{author_init}</div>'
                '<div>'
                f'<div class="author-name">{r.get("author","Unknown")}</div>'
                f'<div class="author-time">📅 {r.get("timestamp","N/A")}</div>'
                '</div></div>'
                f'<span class="post-num-badge">POST #{r["id"]}</span>'
                '</div>'
                '<div class="card-body">'
                + post_url_html +
                '<div class="section-head">📝 Content</div>'
                f'<div class="post-text">{safe_content}</div>'
                '<div class="reactions-row">'
                f'<div class="reaction-badge">👍 <span class="r-num">{rx.get("total","0")}</span> Reactions</div>'
                f'<div class="reaction-badge">💬 <span class="r-num">{rx.get("comments","–")}</span> Comments</div>'
                f'<div class="reaction-badge">↗️ <span class="r-num">{rx.get("shares","–")}</span> Shares</div>'
                '</div>'
                + cmts_html +
                '</div>'
                '<div class="card-footer">'
                f'<span class="meta-chip">📝 <span>{r.get("word_count",0)} words</span></span>'
                f'<span class="meta-chip">🔤 <span>{r.get("char_count",0)} chars</span></span>'
                f'<span class="meta-chip">🕐 <span>{r.get("scraped_at","")}</span></span>'
                '</div></div>'
            )
            st.markdown(card, unsafe_allow_html=True)

            # Render images BELOW the card using st.image (avoids all HTML escaping issues)
            if imgs:
                st.markdown('<div class="section-head" style="margin-left:4px;">📸 Images</div>',
                            unsafe_allow_html=True)
                img_cols = st.columns(min(len(imgs), 4))
                for idx, src in enumerate(imgs):
                    with img_cols[idx % 4]:
                        try:
                            st.image(src, use_container_width=True)
                        except Exception:
                            st.caption(f"[img {idx+1}]")
                st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)

        else:
            # ── GENERIC card (Groups / Pages / People / Events…) ──
            imgs   = r.get("images", [])
            meta_d = r.get("meta", {}).get("details", [])

            img_html = ""  # images rendered separately via st.image below

            meta_html = ""
            if meta_d:
                chips = "".join(
                    f'<span class="meta-chip"><span>{str(d).replace("<","&lt;")[:50]}</span></span>'
                    for d in meta_d if d
                )
                meta_html = f'<div class="reactions-row">{chips}</div>'

            link_html = ""
            if r.get("link"):
                safe_url = r["link"].replace('"', "")
                link_html = f'<a class="post-url-link" href="{safe_url}" target="_blank">🔗 {safe_url}</a>'

            desc_html = ""
            if r.get("description"):
                safe_desc = r["description"].replace("<","&lt;").replace(">","&gt;")
                desc_html = f'<div class="section-head">ℹ️ Details</div><div class="post-text" style="font-size:13px;">{safe_desc}</div>'

            safe_title = r.get("title", "Untitled").replace("<", "&lt;").replace(">", "&gt;")
            title_init = safe_title[0].upper() if safe_title else "?"

            card = (
                '<div class="post-card">'
                '<div class="card-header">'
                '<div class="author-block">'
                f'<div class="author-avatar">{title_init}</div>'
                '<div>'
                f'<div class="author-name">{safe_title}</div>'
                f'<div class="author-time">🕐 {r.get("scraped_at", "")}</div>'
                '</div></div>'
                f'<span class="post-num-badge">{active_cat["icon"]} #{r["id"]}</span>'
                '</div>'
                '<div class="card-body">'
                + link_html
                + desc_html
                + meta_html
                + '</div></div>'
            )
            st.markdown(card, unsafe_allow_html=True)

            # Render images below the card
            if imgs:
                st.markdown('<div class="section-head" style="margin-left:4px;">📸 Images</div>',
                            unsafe_allow_html=True)
                img_cols = st.columns(min(len(imgs), 4))
                for idx, src in enumerate(imgs):
                    with img_cols[idx % 4]:
                        try:
                            st.image(src, use_container_width=True)
                        except Exception:
                            st.caption(f"[img {idx+1}]")
                st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)

elif logs:
    with st.expander("🖥️ Scrape Log", expanded=True):
        st.markdown('<div class="log-panel">' + "<br>".join(logs) + "</div>",
                    unsafe_allow_html=True)

else:
    # Empty state
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">⚡</div>
        <div class="empty-title">Ready to scrape</div>
        <div class="empty-sub">
            Upload your <b>cookies.json</b>, choose a category from the sidebar,<br>
            enter a query, and hit <b>Start Scraping</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
