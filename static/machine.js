(function () {
    "use strict";
    var C = window.CANVAS, T = C.t, B = C.blocks;
    var state = JSON.parse(JSON.stringify(C.boxes));      // title, tagline, theme + one text per box
    var active = null, finished = false, dirty = false, saveTimer = null;
    var loadSuggestions = function () {};
    var seen = {};
    var $ = function (id) { return document.getElementById(id); };
    var edText = $("ed-text"), edDone = $("ed-done");
    var isPhone = window.matchMedia("(max-width: 820px)");

    function words(s) { s = (s || "").trim(); return s ? s.split(/\s+/).length : 0; }
    function fmt(s, o) { return s.replace(/\{(\w+)\}/g, function (_, k) { return o[k]; }); }
    function post(url, data) {
        return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
            .then(function (r) { return r.json().then(function (j) { if (!r.ok) { j.status = r.status; throw j; } return j; }); });
    }
    function track(type, detail) { try { post("/api/event", { pid: C.pid, page: "machine", type: type, detail: detail }).catch(function () {}); } catch (e) {} }
    function blockOf(key) { return B.filter(function (b) { return b.key === key; })[0]; }
    function online(key) { return words(state[key]) >= C.minWords; }
    function onlineCount() { return B.filter(function (b) { return online(b.key); }).length; }
    function filled() { return B.filter(function (b) { return (state[b.key] || "").trim(); }).length; }
    function themeColor() {
        var t = C.themes.filter(function (x) { return x.key === state.theme; })[0] || C.themes[0]; return t.color;
    }

    // ---- tabs (phone) -----------------------------------------------------------------------
    function setTab(tab) {
        document.body.setAttribute("data-tab", tab);
        var el = $("tab-" + tab); if (el) { el.classList.remove("dot"); }
        Array.prototype.forEach.call(document.querySelectorAll(".tabbar button"), function (b) {
            b.setAttribute("aria-selected", b.id === "tab-" + tab ? "true" : "false");
        });
        if (tab === "machine") { setTimeout(drawWires, 30); }
    }
    Array.prototype.forEach.call(document.querySelectorAll(".tabbar button"), function (b) {
        b.addEventListener("click", function () { setTab(b.getAttribute("data-tab")); });
    });
    setTab("machine");

    // ---- the machine: nine pods joined by wires, snake order 1-2-3-6-5-4-7-8-9 ---------------------
    var SNAKE = [0, 1, 2, 5, 4, 3, 6, 7, 8];
    var podsEl = $("pods"), podEls = {};
    function buildPods() {
        podsEl.innerHTML = "";
        B.forEach(function (b, i) {
            var el = document.createElement("button"); el.type = "button"; el.className = "pod c-" + b.key; el.setAttribute("data-key", b.key);
            el.innerHTML = '<span class="pod-head"><span class="pod-ico"></span><span class="pod-title"></span><span class="pod-state"></span></span>' +
                           '<span class="pod-text"></span><span class="gear" aria-hidden="true"></span>';
            el.querySelector(".pod-ico").textContent = b.icon || "";
            el.querySelector(".pod-title").textContent = b.title;
            el.addEventListener("click", function () { setActive(b.key, true); });
            podsEl.appendChild(el); podEls[b.key] = el;
        });
    }
    function renderPods(popKey) {
        B.forEach(function (b) {
            var el = podEls[b.key], on = online(b.key);
            el.classList.toggle("on", on); el.classList.toggle("active", b.key === active);
            el.querySelector(".pod-state").textContent = on ? T.m_online : T.m_offline;
            el.querySelector(".pod-text").textContent = (state[b.key] || "").trim();
            if (popKey === b.key) { el.classList.remove("pop"); void el.offsetWidth; el.classList.add("pop"); }
        });
        drawWires(); renderPower();
    }
    function renderPower() {
        var n = onlineCount();
        $("barfill").style.width = Math.round(100 * n / B.length) + "%";
        $("progtext").textContent = fmt(T.m_parts, { n: n, total: B.length });
        document.documentElement.style.setProperty("--slide", themeColor());
        $("startbtn").classList.toggle("ready", filled() >= C.minFilled);
        Array.prototype.forEach.call(document.querySelectorAll(".swatch"), function (s) {
            s.setAttribute("aria-checked", s.getAttribute("data-theme") === state.theme ? "true" : "false");
        });
    }

    var NS = "http://www.w3.org/2000/svg", wires = $("wires"), machine = $("machine"), liveSegments = 0;
    function drawWires() {
        var box = machine.getBoundingClientRect();
        if (!box.width || !box.height) { return; }
        wires.setAttribute("width", box.width); wires.setAttribute("height", box.height);
        wires.setAttribute("viewBox", "0 0 " + box.width + " " + box.height);
        while (wires.firstChild) { wires.removeChild(wires.firstChild); }
        var centre = function (key) { var r = podEls[key].getBoundingClientRect(); return [r.left - box.left + r.width / 2, r.top - box.top + r.height / 2]; };
        liveSegments = 0;
        for (var i = 0; i < SNAKE.length - 1; i++) {
            var a = B[SNAKE[i]], b = B[SNAKE[i + 1]];
            var p = centre(a.key), q = centre(b.key), live = online(a.key) && online(b.key);
            var d = "M" + p[0] + " " + p[1] + " L" + q[0] + " " + q[1];
            var line = document.createElementNS(NS, "path"); line.setAttribute("d", d);
            line.setAttribute("class", "wire" + (live ? " live" : "")); wires.appendChild(line);
            if (live) {
                liveSegments += 1;
            }
        }
    }
    if (window.ResizeObserver) { new ResizeObserver(function () { drawWires(); }).observe(machine); }
    window.addEventListener("resize", drawWires);


    // ---- editor -----------------------------------------------------------------------------
    function renderEditor() {
        var b = blockOf(active), i = B.indexOf(b);
        $("ed-empty").hidden = true; $("ed-body").hidden = false;
        $("ed-step").textContent = (i + 1) + " / " + B.length + (b.lean ? "  ·  " + b.lean : "");
        $("ed-title").textContent = (b.icon ? b.icon + " " : "") + b.title;
        try { window.dispatchEvent(new CustomEvent("boxchange", { detail: b.key })); } catch (e) {}
        $("ed-question").textContent = b.question;
        if (edText.value !== state[active]) { edText.value = state[active]; }
        updateEditorState();
        document.querySelector(".m-edit").className = "col col-edit m-edit c-" + b.key;
        if (!C.ai) {
            $("guide-empty").hidden = true; $("guide-think-title").hidden = false;
            var ul = $("guide-tips"); ul.innerHTML = "";
            b.tips.forEach(function (t) { var li = document.createElement("li"); li.textContent = t; ul.appendChild(li); });
            $("guide-ex-title").textContent = fmt(T.guide_example, { name: C.exampleBusiness });
            $("guide-example").textContent = b.example;
        }
    }
    function updateEditorState() {
        var w = words(edText.value);
        $("ed-hint").textContent = w < C.minWords ? fmt(T.editor_hint, { n: C.minWords }) : "";
        edDone.disabled = false;
    }
    function setActive(key, focus) {
        if (active) { save(); }
        active = key;
        track("box_opened", key);
        renderEditor(); renderPods();
        if (isPhone.matches && focus) { setTab("write"); }
        if (focus && !isPhone.matches) { edText.focus(); }
        if (C.ai) { loadSuggestions(key); }
    }
    function onEdit() {
        var was = online(active);
        state[active] = edText.value;
        updateEditorState(); changed();
        renderPods(!was && online(active) ? active : null);
        if (!was && online(active)) { toast(T.unlocked.replace("{name}", blockOf(active).title)); happy(); }
    }
    edText.addEventListener("input", onEdit);
    edText.addEventListener("paste", function (e) {
        var t = (e.clipboardData || window.clipboardData); track("paste", active + ":" + (t ? t.getData("text").length : "?"));
    });
    edDone.addEventListener("click", function () {
        track("box_done", active); save();
        if (isPhone.matches) { setTab("machine"); }
    });

    $("title").addEventListener("input", function (e) { state.title = e.target.value; changed(); });
    $("tagline").addEventListener("input", function (e) { state.tagline = e.target.value; changed(); });
    Array.prototype.forEach.call(document.querySelectorAll(".swatch"), function (s) {
        s.addEventListener("click", function () { state.theme = s.getAttribute("data-theme"); track("colour", state.theme); renderPower(); changed(); });
    });

    // ---- autosave ---------------------------------------------------------------------------
    function save() {
        if (finished || !dirty) { return Promise.resolve(); }
        dirty = false;
        return post("/api/canvas", { pid: C.pid, boxes: state }).then(function () { $("saved").textContent = T.saved; })
            .catch(function () { dirty = true; });
    }
    function changed() {
        dirty = true; $("saved").textContent = "";
        if (!saveTimer) { saveTimer = setTimeout(function () { saveTimer = null; save(); }, 1500); }
    }
    function saveNow() {
        if (finished || !dirty) { return; }
        dirty = false;
        try { fetch("/api/canvas", { method: "POST", keepalive: true, headers: { "Content-Type": "application/json" },
                                     body: JSON.stringify({ pid: C.pid, boxes: state }) }); } catch (e) { dirty = true; }
    }
    document.addEventListener("copy", function () { var s = String(window.getSelection() || ""); if (s) { track("copy", s.length); } });
    document.addEventListener("visibilitychange", function () { track(document.hidden ? "tab_hidden" : "tab_visible"); if (document.hidden) { saveNow(); } });
    window.addEventListener("pagehide", saveNow);

    // ---- toast, modal -----------------------------------------------------------------------
    var toastTimer = null;
    function toast(text) {
        var t = $("toast"); t.textContent = text; t.hidden = false;
        clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.hidden = true; }, 2600);
    }
    var overlay = $("overlay");
    function modal(title, text, buttons) {
        $("modal-title").textContent = title; $("modal-text").textContent = text;
        var holder = $("modal-buttons"); holder.innerHTML = "";
        buttons.forEach(function (b) {
            var el = document.createElement("button"); el.type = "button";
            el.className = "btn small" + (b.ghost ? " ghost" : ""); el.textContent = b.label;
            el.onclick = function () { overlay.hidden = true; if (b.fn) { b.fn(); } };
            holder.appendChild(el);
        });
        overlay.hidden = false; if (holder.firstChild) { holder.firstChild.focus(); }
    }

    // ---- start the machine: boot animation, then the prototype ---------------------------------
    var booting = false;
    function startMachine() {
        if (finished || booting) { return; }
        if (filled() < C.minFilled) { modal(T.m_start, fmt(T.m_need, { n: C.minFilled }), [{ label: T.m_close }]); return; }
        save(); booting = true; track("machine_started", onlineCount());
        var boot = $("boot"), lines = $("boot-lines"), fill = $("boot-fill"), rain = $("boot-coins");
        boot.style.setProperty("--slide", themeColor());
        lines.innerHTML = ""; rain.innerHTML = ""; fill.style.width = "0";
        boot.hidden = false;
        var steps = [T.m_boot1, T.m_boot2, T.m_boot3];
        steps.forEach(function (txt, i) {
            setTimeout(function () {
                var p = document.createElement("p"); p.textContent = txt; p.className = i === steps.length - 1 ? "ready" : "";
                lines.appendChild(p); fill.style.width = Math.round(100 * (i + 1) / steps.length) + "%";
                if (i === steps.length - 1) { makeRain(rain); }
            }, 700 + i * 1500);
        });
        setTimeout(function () { boot.hidden = true; booting = false; openProto(); }, 6000);
    }
    function makeRain(el) {
        for (var i = 0; i < 28; i++) {
            var c = document.createElement("span"); c.className = "drop";
            c.style.left = (Math.random() * 100) + "%"; c.style.animationDelay = (Math.random() * 1.4) + "s";
            c.style.animationDuration = (1.4 + Math.random() * 1.2) + "s"; el.appendChild(c);
        }
    }
    $("startbtn").addEventListener("click", startMachine);

    // ---- the prototype: a small business website built only from the participant's own words ----------------------
    function esc(x) { return String(x).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
    function paras(x) { return x.split(/\n+/).map(function (l) { return l.trim(); }).filter(Boolean).map(function (l) { return "<p>" + esc(l) + "</p>"; }).join(""); }
    function slug(x) { return (x || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 28) || "your-business"; }
    function part(id, heading, key, cls) {
        var t = (state[key] || "").trim();
        return '<section class="s ' + (cls || "") + '" id="' + id + '"><h2>' + esc(heading) + "</h2>" + (t ? paras(t) : '<p class="empty">' + esc(T.m_empty_proto) + "</p>") + "</section>";
    }
    var SITE_CSS = ".site{font:16px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1a1a24;background:#fff}" +
        ".site *{box-sizing:border-box}.site nav{display:flex;align-items:center;gap:22px;padding:16px 28px;border-bottom:1px solid #ececf3}" +
        ".site .brand{font-weight:800;font-size:1.1rem;letter-spacing:-.02em;margin-right:auto;overflow-wrap:anywhere}.site nav a{color:#555;text-decoration:none;font-size:14px}" +
        ".site .cta{display:inline-block;background:var(--a);color:#fff;border:0;border-radius:10px;padding:11px 20px;font:inherit;font-weight:600;cursor:default;text-decoration:none}" +
        ".site .hero{padding:68px 28px 58px;background:linear-gradient(180deg,color-mix(in srgb,var(--a) 13%,#fff),#fff)}" +
        ".site h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.08;letter-spacing:-.035em;margin:0 0 14px;max-width:16em;overflow-wrap:anywhere}" +
        ".site .hero p{font-size:1.15rem;color:#4b4b5c;max-width:34em;margin:0 0 24px;overflow-wrap:anywhere}" +
        ".site .cols{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.site .s{padding:38px 28px;border-top:1px solid #f0f0f5}" +
        ".site .s h2{font-size:1.45rem;letter-spacing:-.02em;margin:0 0 10px}.site .s p{margin:0 0 8px;max-width:40em;overflow-wrap:anywhere}" +
        ".site .empty{color:#a3a3b2;font-style:italic}.site .quote{background:var(--a);border-top:0}.site .quote h2,.site .quote p{color:#fff}" +
        ".site .quote p{font-size:1.25rem;line-height:1.45}.site footer{padding:26px 28px;background:#14141c;color:#a8a8b8;font-size:13px}" +
        ".site.narrow nav{padding:14px 18px}.site.narrow nav a{display:none}.site.narrow .hero{padding:44px 18px 38px}.site.narrow .cols{grid-template-columns:1fr}.site.narrow .s{padding:30px 18px}" +
        "@media(max-width:640px){.site nav{padding:14px 18px}.site nav a{display:none}.site .hero{padding:44px 18px 38px}.site .cols{grid-template-columns:1fr}.site .s{padding:30px 18px}}";
    function siteBody() {
        var name = (state.title || "").trim() || "Your business", tag = (state.tagline || "").trim(), uvp = (state.uvp || "").trim();
        return '<nav><span class="brand">' + esc(name) + '</span><a href="#what">What we do</a><a href="#price">Pricing</a><a href="#find">Find us</a><span class="cta">Get in touch</span></nav>' +
            '<header class="hero"><h1>' + esc(tag || name) + "</h1>" + (uvp ? "<p>" + esc(uvp.split(/\n+/)[0]) + "</p>" : "") + '<span class="cta">Get in touch</span></header>' +
            '<div class="cols">' + part("problem", "The problem", "problem") + part("what", "What we do", "solution") + part("who", "Who it is for", "customers") + part("price", "Pricing", "income") + "</div>" +
            part("find", "How to find us", "channels") + ((state.edge || "").trim() ? part("edge", "Why us", "edge", "quote") : "") +
            "<footer>" + esc(name) + " &middot; Made in the Entrepreneurial Project Challenge</footer>";
    }
    function buildProto() {
        var s = $("proto-site"); s.innerHTML = ""; s.style.setProperty("--slide", themeColor());
        var name = (state.title || "").trim();
        s.innerHTML = "<style>" + SITE_CSS + "</style>" +
            '<div class="browser"><div class="browser-bar"><i></i><i></i><i></i><span class="addr">www.' + esc(slug(name)) + '.example</span></div>' +
            '<div class="site" style="--a:' + esc(themeColor()) + '">' + siteBody() + "</div></div>";
        var notes = $("proto-notes"); notes.innerHTML = "";
        var rows = ["costs", "metrics"].map(function (k) { var t = (state[k] || "").trim(); return t ? "<div><b>" + esc(blockOf(k).title) + ":</b> " + esc(t) + "</div>" : ""; }).join("");
        if (rows) { notes.innerHTML = "<h3>" + esc(T.m_notes) + "</h3>" + rows; }
        setDevice(deviceNarrow);
    }
    var deviceNarrow = false;
    function setDevice(narrow) {
        deviceNarrow = narrow;
        var site = document.querySelector("#proto-site .site"), box = $("proto-site");
        if (site) { site.classList.toggle("narrow", narrow); } box.classList.toggle("phone", narrow);
        $("dev-desktop").setAttribute("aria-pressed", narrow ? "false" : "true"); $("dev-phone").setAttribute("aria-pressed", narrow ? "true" : "false");
    }
    $("dev-desktop").addEventListener("click", function () { setDevice(false); track("prototype_device", "desktop"); });
    $("dev-phone").addEventListener("click", function () { setDevice(true); track("prototype_device", "phone"); });
    $("proto-download").addEventListener("click", function () {
        var name = (state.title || "").trim() || "Your business";
        var html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + esc(name) +
            "</title><style>body{margin:0}" + SITE_CSS + '</style></head><body><div class="site" style="--a:' + esc(themeColor()) + '">' + siteBody() + "</div></body></html>";
        var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([html], { type: "text/html" })); a.download = slug(name) + "-project.html";
        document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); track("prototype_download");
    });
    function openProto() {
        buildProto(); $("proto").hidden = false; track("prototype_viewed");
    }
    $("proto-back").addEventListener("click", function () { $("proto").hidden = true; track("prototype_back"); });
    var finish = $("finish");
    finish.addEventListener("click", function () {
        if (finished) { return; }
        finish.disabled = true;
        finishUp("button").catch(function () { finish.disabled = false; modal(T.m_finish, T.m_error || "Something went wrong. Please try again.", [{ label: T.m_close }]); });
    });


    // ---- hand in and timer ------------------------------------------------------------------
    function finishUp(how) {
        if (finished) { return Promise.resolve(); }
        return post("/api/canvas/submit", { pid: C.pid, boxes: state, how: how }).then(function () {
            finished = true; location.href = C.doneUrl;
        });
    }
    var left = C.secondsLeft, timerEl = $("timer");
    function tick() {
        var m = Math.floor(left / 60), s = left % 60;
        timerEl.textContent = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
        timerEl.classList.toggle("low", left <= 60);
        if (left <= 0) {
            clearInterval(iv);
            modal(T.timeup.split(".")[0], T.timeup, []);
            finishUp("timeout").catch(function () { location.href = C.doneUrl; });
            return;
        }
        left -= 1;
    }
    var iv = setInterval(tick, 1000); tick();

    // ---- Compi, the AI co-founder: an animated character that gives short tips -------------------------
    var happy = function () {};
    if (C.ai) {
        var avatar = $("avatar"), say = $("say"), youEl = $("you"), chipsEl = $("chips"), form = $("chatform"), input = $("chatinput");
        var send = $("send"), busy = false, quickBtns = document.querySelectorAll("[data-quick]");
        var mini = $("mini"), miniSay = $("mini-say");
        var lastMsg = {}, reopens = {}, typer = null, full = "", pending = null, moodTimer = null;
        var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        var setMood = function (m) { avatar.setAttribute("data-mood", m); };
        happy = function () { clearTimeout(moodTimer); setMood("happy"); moodTimer = setTimeout(function () { setMood("idle"); }, 1600); };

        var setIdle = function () { setMood("idle"); };
        var stopVoice = function () {};

        var showChips = function () {
            if (!pending) { return; }
            var p = pending; pending = null; chipsEl.innerHTML = "";
            (p.suggestions || []).forEach(function (sug, idx) {
                var c = document.createElement("button"); c.type = "button"; c.className = "chip";
                var t = document.createElement("span"); t.textContent = sug;
                var a = document.createElement("span"); a.className = "add"; a.textContent = T.ai_use;
                c.appendChild(t); c.appendChild(a);
                c.addEventListener("click", function () { useSuggestion(c, a, sug, p.box || active, idx); });
                chipsEl.appendChild(c);
            });
        };
        var finishTyping = function () {
            clearInterval(typer); typer = null; say.textContent = full; setIdle(); showChips();
        };
        // show a message from Compi: typed out like speech (tap the bubble to skip), then the suggestion chips
        var speak = function (text, suggestions, boxKey, instant, aloud) {
            clearInterval(typer); full = text; chipsEl.innerHTML = ""; pending = { suggestions: suggestions || [], box: boxKey };
            if (miniSay) { miniSay.textContent = text; mini.hidden = false; }
            if (instant || reduced) { say.textContent = text; setIdle(); showChips(); return; }
            say.textContent = ""; setMood("talking"); var i = 0;
            typer = setInterval(function () { i += 2; say.textContent = text.slice(0, i); if (i >= text.length) { finishTyping(); } }, 26);
        };
        $("speech").addEventListener("click", function () { if (typer) { finishTyping(); } });
        var notifyAI = function () {
            if (isPhone.matches && document.body.getAttribute("data-tab") !== "side") {
                var t = $("tab-side"); if (t) { t.classList.add("dot"); }
                if (document.body.getAttribute("data-tab") === "write") { toast(T.ai_new); }
            }
        };
        if (mini) { mini.addEventListener("click", function () { setTab("side"); }); }

        // a chip is Compi's quick move answered: it goes into the plan AND is sent to Compi, who reacts and moves the game on
        var useSuggestion = function (chip, addEl, text, boxKey, idx) {
            if (chip.classList.contains("used") || busy) { return; }
            if (!boxKey) {                     // the opening names parts of the map: tapping one opens that part and Compi gives its tip
                var hit = B.filter(function (b) { return b.title.toLowerCase() === String(text).trim().toLowerCase(); })[0];
                if (hit) {
                    Array.prototype.forEach.call(chipsEl.querySelectorAll(".chip"), function (c) { c.classList.add("used"); });
                    addEl.textContent = T.ai_used; track("suggestion_used", "brief:" + hit.key + ":" + idx); happy();
                    setActive(hit.key, true);
                    return;
                }
            }
            if (boxKey) {                      // otherwise the chip only answers Compi
                if (boxKey !== active) { setActive(boxKey, false); }
                var cur = edText.value.trim();
                edText.value = cur ? cur + "\n" + text : text;
            }
            Array.prototype.forEach.call(chipsEl.querySelectorAll(".chip"), function (c) { c.classList.add("used"); });
            addEl.textContent = T.ai_used;
            track("suggestion_used", (boxKey || "brief") + ":" + idx + ":" + text.length);
            if (boxKey) { onEdit(); }
            happy();
            ask(text, "choice");
        };
        var setBusy = function (v) { busy = v; send.disabled = v; Array.prototype.forEach.call(quickBtns, function (b) { b.disabled = v; }); };
        var thinking = function () { stopVoice(); clearInterval(typer); typer = null; say.textContent = ""; chipsEl.innerHTML = ""; pending = null; setMood("thinking"); };

        // restore the stored conversation: Compi shows her latest message
        var latest = null;
        C.history.forEach(function (m) {
            if (m.role !== "assistant") { return; }
            latest = m;
            if (m.kind === "auto" || m.kind === "reopen") { lastMsg[m.box] = m; seen[m.box] = true; }
            if (m.kind === "reopen") { reopens[m.box] = (reopens[m.box] || 0) + 1; }
        });
        // a new AI participant gets a short opening about THEIR idea (what shapes it); the static greeting stays as the fallback
        var needBrief = !finished && !C.history.some(function (m) { return m.kind === "brief" || m.kind === "auto" || m.kind === "reopen" || m.kind === "reply"; });
        if (needBrief) {
            thinking();
            post("/api/brief", { pid: C.pid, boxes: state }).then(function (r) {
                if (active) { return; }                    // they already opened a part: the opening is stored, not shown
                speak(r.reply, r.suggestions, null); notifyAI();
            }).catch(function () {
                if (!active && latest) { speak(latest.content, latest.suggestions, latest.box, true); }
            });
        } else if (latest) { speak(latest.content, latest.suggestions, latest.box, true, C.history.length <= 1); }

        var lastText = {};
        B.forEach(function (b) { if (lastMsg[b.key]) { lastText[b.key] = state[b.key] || ""; } });
        loadSuggestions = function (key) {
            if (finished) { return; }
            var refresh = false;
            if (seen[key]) {
                var txt = state[key] || "";
                refresh = words(txt) >= 3 && txt !== lastText[key] && (reopens[key] || 0) < 3;
                if (!refresh) { if (lastMsg[key]) { speak(lastMsg[key].content, lastMsg[key].suggestions, key, true); } return; }
            }
            seen[key] = true; lastText[key] = state[key] || "";
            thinking();
            post("/api/suggest", { pid: C.pid, box: key, boxes: state, refresh: refresh }).then(function (r) {
                if (refresh) { reopens[key] = (reopens[key] || 0) + 1; }
                lastMsg[key] = { content: r.reply, suggestions: r.suggestions };
                if (active !== key) { return; }            // they moved on while Compi was thinking: it is stored, shown when they return
                speak(r.reply, r.suggestions, key); notifyAI();
            }).catch(function (err) {
                if (refresh) { reopens[key] = 3; setMood("idle"); if (lastMsg[key]) { speak(lastMsg[key].content, lastMsg[key].suggestions, key, true); } return; }
                seen[key] = false; speak((err && err.error) || T.ai_error, [], key, true);
            });
        };
        var ask = function (text, quick) {
            if (!text || busy || finished) { return; }
            setBusy(true); youEl.textContent = text; youEl.hidden = false; thinking();
            post("/api/chat", { pid: C.pid, message: text, box: active || B[0].key, boxes: state, quick: quick || "" }).then(function (r) {
                speak(r.reply, r.suggestions, active || B[0].key); notifyAI();
            }).catch(function (err) {
                speak((err && err.error) || T.ai_error, [], active || B[0].key, true);
            }).then(function () { setBusy(false); });
        };
        var grow = function () { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 96) + "px"; };
        input.addEventListener("input", grow);
        input.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
        form.addEventListener("submit", function (e) { e.preventDefault(); var t = input.value.trim(); input.value = ""; grow(); ask(t, ""); });
        Array.prototype.forEach.call(quickBtns, function (b) {
            b.addEventListener("click", function () {
                var kind = b.getAttribute("data-quick");
                ask(kind === "more" ? T.ai_quick_more : T.ai_quick_feedback, kind);
            });
        });
    }


    // ---- start ------------------------------------------------------------------------------
    buildPods(); renderPods();
    window.CANVAS_READY = "2026-11-10";
})();
