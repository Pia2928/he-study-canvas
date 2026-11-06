(function () {
    "use strict";
    var C = window.CANVAS, T = C.t, B = C.blocks;
    var state = clone(C.boxes);                 // title, tagline, theme + one text per box
    var active = null, finished = false, dirty = false, saveTimer = null;
    var loadSuggestions = function () {};        // set below for the AI group
    var seen = {};                              // boxes whose AI suggestions are already in the thread
    var $ = function (id) { return document.getElementById(id); };
    var gridEl = $("grid"), edText = $("ed-text"), edDone = $("ed-done");

    function clone(o) { return JSON.parse(JSON.stringify(o)); }
    function words(s) { s = (s || "").trim(); return s ? s.split(/\s+/).length : 0; }
    function fmt(s, o) { return s.replace(/\{(\w+)\}/g, function (_, k) { return o[k]; }); }
    function post(url, data) {
        return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
            .then(function (r) { return r.json().then(function (j) { if (!r.ok) { j.status = r.status; throw j; } return j; }); });
    }
    function track(type, detail) {
        try { post("/api/event", { pid: C.pid, page: "canvas", type: type, detail: detail }).catch(function () {}); } catch (e) {}
    }
    function themeColor() {
        var t = C.themes.filter(function (x) { return x.key === state.theme; })[0] || C.themes[0];
        return t.color;
    }

    // ---- progress and unlocking -------------------------------------------------------------
    function unlockedCount() {          // box i is open when all boxes before it have enough words
        var n = 1;
        for (var i = 0; i < B.length - 1; i++) {
            if (words(state[B[i].key]) >= C.minWords) { n += 1; } else { break; }
        }
        return n;
    }
    function filled() { return B.filter(function (b) { return state[b.key].trim(); }).length; }
    function done() { return B.filter(function (b) { return words(state[b.key]) >= C.minWords; }).length; }

    function renderProgress() {
        var d = done();
        $("barfill").style.width = Math.round(100 * d / B.length) + "%";
        $("progtext").textContent = fmt(T.progress, { n: d, total: B.length });
        document.documentElement.style.setProperty("--slide", themeColor());
        Array.prototype.forEach.call(document.querySelectorAll(".swatch"), function (s) {
            s.setAttribute("aria-checked", s.getAttribute("data-theme") === state.theme ? "true" : "false");
        });
    }

    function renderGrid(popKey) {
        var open = unlockedCount();
        gridEl.innerHTML = "";
        B.forEach(function (b, i) {
            var locked = i >= open;
            var el = document.createElement("button");
            el.type = "button";
            el.className = "card" + (b.hybrid ? " hybrid" : "") + (locked ? " locked" : "") +
                (b.key === active ? " active" : "") + (words(state[b.key]) >= C.minWords ? " done" : "") +
                (popKey === b.key ? " pop" : "");
            el.disabled = false;
            el.setAttribute("aria-disabled", locked ? "true" : "false");
            var top = document.createElement("div"); top.className = "card-top";
            var num = document.createElement("span"); num.className = "num";
            num.textContent = locked ? "" : (words(state[b.key]) >= C.minWords ? "✓" : String(i + 1));
            if (locked) { num.innerHTML = '<span class="lockicon" aria-hidden="true">🔒</span>'; }
            var h = document.createElement("h3"); h.textContent = b.title;
            top.appendChild(num); top.appendChild(h);
            if (b.hybrid) { var tag = document.createElement("span"); tag.className = "tag"; tag.textContent = T.hybrid_label || ""; if (tag.textContent) { top.appendChild(tag); } }
            el.appendChild(top);
            var body = document.createElement("div");
            if (locked) {
                body.className = "card-empty"; body.textContent = fmt(T.locked, { prev: B[Math.max(0, i - 1)].title });
            } else if (state[b.key].trim()) {
                body.className = "card-text"; body.textContent = state[b.key];
            } else {
                body.className = "card-empty"; body.textContent = T.empty_box;
            }
            el.appendChild(body);
            if (!locked) { el.addEventListener("click", function () { setActive(b.key, true); }); }
            gridEl.appendChild(el);
        });
    }

    // ---- editor -----------------------------------------------------------------------------
    function blockOf(key) { return B.filter(function (b) { return b.key === key; })[0]; }
    function indexOf(key) { return B.indexOf(blockOf(key)); }

    function renderEditor() {
        var b = blockOf(active), i = indexOf(active);
        $("ed-step").textContent = (i + 1) + " / " + B.length;
        $("ed-title").textContent = b.title;
        $("ed-question").textContent = b.question;
        if (edText.value !== state[active]) { edText.value = state[active]; }
        edDone.textContent = i === B.length - 1 ? T.done_last : T.done_next;
        updateEditorState();
        if (!C.ai) {
            var ul = $("guide-tips"); ul.innerHTML = "";
            b.tips.forEach(function (t) { var li = document.createElement("li"); li.textContent = t; ul.appendChild(li); });
            $("guide-ex-title").textContent = fmt(T.guide_example, { name: C.exampleBusiness });
            $("guide-example").textContent = b.example;
        }
    }
    function updateEditorState() {
        var w = words(edText.value);
        edDone.disabled = w < C.minWords;
        $("ed-hint").textContent = w < C.minWords ? fmt(T.editor_hint, { n: C.minWords }) : "";
    }

    function setActive(key, focus) {
        if (active) { save(); }
        active = key;
        track("box_opened", key);
        renderGrid(); renderEditor(); renderProgress();
        if (focus) { edText.focus(); }
        if (C.ai) { loadSuggestions(key); }
    }

    function onEdit() {
        state[active] = edText.value;
        updateEditorState(); changed();
        var before = unlockedBefore;
        var now = unlockedCount();
        unlockedBefore = now;
        renderProgress();
        if (!celebrated && done() === B.length) { celebrated = true; toast(T.all_done); }
        if (now > before) {
            toast(fmt(T.unlocked, { name: B[now - 1].title }));
            renderGrid(B[now - 1].key);
        } else { renderGrid(); }
    }
    var unlockedBefore = unlockedCount();
    edText.addEventListener("input", onEdit);
    edText.addEventListener("paste", function (e) {
        var t = (e.clipboardData || window.clipboardData); track("paste", active + ":" + (t ? t.getData("text").length : "?"));
    });
    edText.addEventListener("keydown", function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !edDone.disabled) { e.preventDefault(); edDone.click(); }
    });
    var celebrated = false;
    edDone.addEventListener("click", function () {
        track("box_done", active);
        var i = indexOf(active);
        if (i === B.length - 1) { openPreview(); return; }
        setActive(B[i + 1].key, true);
    });

    // ---- name, tagline, colour --------------------------------------------------------------
    $("title").addEventListener("input", function (e) { state.title = e.target.value; changed(); });
    $("tagline").addEventListener("input", function (e) { state.tagline = e.target.value; changed(); });
    Array.prototype.forEach.call(document.querySelectorAll(".swatch"), function (s) {
        s.addEventListener("click", function () { state.theme = s.getAttribute("data-theme"); track("colour", state.theme); renderProgress(); changed(); });
    });

    // ---- autosave ---------------------------------------------------------------------------
    function save() {
        if (finished || !dirty) { return Promise.resolve(); }
        dirty = false;
        return post("/api/canvas", { pid: C.pid, boxes: state }).then(function () { $("saved").textContent = T.saved; })
            .catch(function () { dirty = true; });
    }
    // Save at most 1.5 s after the first unsaved change (not reset by further typing), so fast typing is still saved.
    function changed() {
        dirty = true; $("saved").textContent = "";
        if (!saveTimer) { saveTimer = setTimeout(function () { saveTimer = null; save(); }, 1500); }
    }
    function saveNow() {          // used when the page is hidden or closed: keepalive lets the request finish
        if (finished || !dirty) { return; }
        dirty = false;
        try {
            fetch("/api/canvas", { method: "POST", keepalive: true, headers: { "Content-Type": "application/json" },
                                   body: JSON.stringify({ pid: C.pid, boxes: state }) });
        } catch (e) { dirty = true; }
    }
    document.addEventListener("copy", function () { var s = String(window.getSelection() || ""); if (s) { track("copy", s.length); } });
    document.addEventListener("visibilitychange", function () {
        track(document.hidden ? "tab_hidden" : "tab_visible"); if (document.hidden) { saveNow(); }
    });
    window.addEventListener("pagehide", saveNow);

    // ---- toast, modal, preview --------------------------------------------------------------
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
    function openPreview() {
        var s = $("slide"); s.innerHTML = ""; s.style.setProperty("--slide", themeColor());
        var head = document.createElement("div"); head.className = "slide-head";
        var h1 = document.createElement("h1"); h1.textContent = state.title || "";
        head.appendChild(h1);
        if (state.tagline) { var p = document.createElement("p"); p.className = "slide-tag"; p.textContent = state.tagline; head.appendChild(p); }
        s.appendChild(head);
        var g = document.createElement("div"); g.className = "slide-grid";
        B.forEach(function (b) {
            var box = document.createElement("section"); box.className = "slide-box";
            var h = document.createElement("h3"); h.textContent = b.title;
            var p = document.createElement("p"); p.textContent = state[b.key].trim() || "—";
            box.appendChild(h); box.appendChild(p); g.appendChild(box);
        });
        s.appendChild(g);
        track("preview_opened"); $("preview").hidden = false;
    }
    $("previewbtn").addEventListener("click", openPreview);
    $("preview-close").addEventListener("click", function () { $("preview").hidden = true; });

    // ---- hand in and timer ------------------------------------------------------------------
    function finish(how) {
        if (finished) { return; }
        return post("/api/canvas/submit", { pid: C.pid, boxes: state, how: how }).then(function () {
            finished = true; location.href = C.doneUrl;
        });
    }
    $("submit").addEventListener("click", function () {
        if (filled() < C.minFilled) { modal(T.confirm_title, T.need_more.replace("{n}", C.minFilled), [{ label: T.confirm_no }]); return; }
        modal(T.confirm_title, T.confirm_text, [{ label: T.confirm_yes, fn: function () { finish("button"); } }, { label: T.confirm_no, ghost: true }]);
    });
    var left = C.secondsLeft, timerEl = $("timer");
    function tick() {
        var m = Math.floor(left / 60), s = left % 60;
        timerEl.textContent = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
        timerEl.classList.toggle("low", left <= 60);
        if (left <= 0) {
            clearInterval(iv);
            modal(T.timeup.split(".")[0], T.timeup, []);
            finish("timeout").catch(function () { location.href = C.doneUrl; });
            return;
        }
        left -= 1;
    }
    var iv = setInterval(tick, 1000); tick();

    // ---- AI co-founder ----------------------------------------------------------------------
    if (C.ai) {
        var thread = $("thread"), form = $("chatform"), input = $("chatinput"), send = $("send"), busy = false;
        var quickBtns = document.querySelectorAll("[data-quick]");
        function scrollDown() { thread.scrollTop = thread.scrollHeight; }
        function addUser(text) {
            var m = document.createElement("div"); m.className = "msg user";
            var b = document.createElement("div"); b.className = "bubble"; b.textContent = text; m.appendChild(b);
            thread.appendChild(m); scrollDown();
        }
        function addAssistant(text, suggestions, boxKey, label) {
            var m = document.createElement("div"); m.className = "msg assistant";
            if (label) { var l = document.createElement("div"); l.className = "boxlabel"; l.textContent = label; m.appendChild(l); }
            var b = document.createElement("div"); b.className = "bubble"; b.textContent = text; m.appendChild(b);
            if (suggestions && suggestions.length) {
                var chips = document.createElement("div"); chips.className = "chips";
                suggestions.forEach(function (sug, idx) {
                    var c = document.createElement("button"); c.type = "button"; c.className = "chip";
                    var t = document.createElement("span"); t.textContent = sug;
                    var a = document.createElement("span"); a.className = "add"; a.textContent = "+ " + T.ai_use;
                    c.appendChild(t); c.appendChild(a);
                    c.addEventListener("click", function () { useSuggestion(c, a, sug, boxKey || active, idx); });
                    chips.appendChild(c);
                });
                m.appendChild(chips);
            }
            thread.appendChild(m); scrollDown(); return m;
        }
        function useSuggestion(chip, addEl, text, boxKey, idx) {
            if (chip.classList.contains("used")) { return; }
            if (boxKey !== active) { setActive(boxKey, false); }
            var cur = edText.value.trim();
            edText.value = cur ? cur + "\n" + text : text;
            chip.classList.add("used"); addEl.textContent = T.ai_used;
            track("suggestion_used", boxKey + ":" + idx + ":" + text.length);
            onEdit(); edText.focus();
        }
        function typing(label) {
            var m = document.createElement("div"); m.className = "msg assistant";
            m.innerHTML = '<div class="typing"><span></span><span></span><span></span><em></em></div>';
            m.querySelector("em").textContent = label || "";
            thread.appendChild(m); scrollDown(); return m;
        }
        function setBusy(v) { busy = v; send.disabled = v; Array.prototype.forEach.call(quickBtns, function (b) { b.disabled = v; }); }

        // restore the stored conversation
        C.history.forEach(function (m) {
            if (m.role === "user") { addUser(m.content); return; }
            var label = m.kind === "auto" && m.box_title ? fmt(T.ai_for_box, { box: m.box_title }) : "";
            addAssistant(m.content, m.suggestions, m.box, label);
            if (m.kind === "auto") { seen[m.box] = true; }
        });

        loadSuggestions = function (key) {
            if (seen[key] || finished) { return; }
            seen[key] = true;
            var b = blockOf(key);
            var wait = typing(fmt(T.ai_thinking, { box: b.title }));
            post("/api/suggest", { pid: C.pid, box: key, boxes: state }).then(function (r) {
                wait.remove(); addAssistant(r.reply, r.suggestions, key, fmt(T.ai_for_box, { box: b.title }));
            }).catch(function (err) {
                seen[key] = false; wait.remove(); addAssistant((err && err.error) || T.ai_error, [], key, "");
            });
        };
        function ask(text, quick) {
            if (!text || busy || finished) { return; }
            setBusy(true); addUser(text);
            var wait = typing("");
            post("/api/chat", { pid: C.pid, message: text, box: active, boxes: state, quick: quick || "" }).then(function (r) {
                wait.remove(); addAssistant(r.reply, r.suggestions, active, "");
            }).catch(function (err) {
                wait.remove(); addAssistant((err && err.error) || T.ai_error, [], active, "");
            }).then(function () { setBusy(false); });
        }
        function grow() { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 120) + "px"; }
        input.addEventListener("input", grow);
        input.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
        form.addEventListener("submit", function (e) { e.preventDefault(); var t = input.value.trim(); input.value = ""; grow(); ask(t, ""); });
        Array.prototype.forEach.call(quickBtns, function (b) {
            b.addEventListener("click", function () {
                var kind = b.getAttribute("data-quick");
                ask(kind === "more" ? T.ai_quick_more : T.ai_quick_feedback, kind);
            });
        });
        scrollDown();
    }

    // ---- start ------------------------------------------------------------------------------
    (function start() {
        var open = unlockedCount();
        var first = B[Math.max(0, open - 1)].key;     // continue at the furthest open box
        active = first;
        renderGrid(); renderEditor(); renderProgress();
        if (C.ai) { loadSuggestions(first); }
    })();
})();
