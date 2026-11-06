(function () {
    "use strict";
    var C = window.CANVAS, T = C.t;
    var titleEl = document.getElementById("title");
    var boxEls = {};
    C.keys.forEach(function (k) { boxEls[k] = document.getElementById("box-" + k); });
    var savedEl = document.getElementById("saved"), timerEl = document.getElementById("timer");
    var submitBtn = document.getElementById("submit");
    var finished = false, dirty = false, saveTimer = null;

    function post(url, data) {
        return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
            .then(function (r) { return r.json().then(function (j) { if (!r.ok) { j.status = r.status; throw j; } return j; }); });
    }
    function boxes() {
        var b = { title: titleEl.value };
        C.keys.forEach(function (k) { b[k] = boxEls[k].value; });
        return b;
    }
    function filled() { return C.keys.filter(function (k) { return boxEls[k].value.trim(); }).length; }
    function track(type, detail) {
        try { post("/api/event", { pid: C.pid, page: "canvas", type: type, detail: detail }).catch(function () {}); } catch (e) {}
    }

    // Autosave: shortly after typing stops
    function save() {
        if (finished || !dirty) { return Promise.resolve(); }
        dirty = false;
        return post("/api/canvas", { pid: C.pid, boxes: boxes() }).then(function () {
            savedEl.textContent = T.saved;
        }).catch(function () { dirty = true; });
    }
    function changed() {
        dirty = true; savedEl.textContent = "";
        clearTimeout(saveTimer); saveTimer = setTimeout(save, 1500);
    }
    titleEl.addEventListener("input", changed);
    C.keys.forEach(function (k) {
        boxEls[k].addEventListener("input", changed);
        boxEls[k].addEventListener("paste", function (e) {
            var t = (e.clipboardData || window.clipboardData); track("paste", k + ":" + (t ? t.getData("text").length : "?"));
        });
    });
    document.addEventListener("copy", function () {
        var s = String(window.getSelection() || ""); if (s) { track("copy", s.length); }
    });
    document.addEventListener("visibilitychange", function () { track(document.hidden ? "tab_hidden" : "tab_visible"); });

    // Modal helper
    var overlay = document.getElementById("overlay");
    function modal(title, text, buttons) {
        document.getElementById("modal-title").textContent = title;
        document.getElementById("modal-text").textContent = text;
        var holder = document.getElementById("modal-buttons"); holder.innerHTML = "";
        buttons.forEach(function (b) {
            var el = document.createElement("button"); el.type = "button";
            el.className = "btn small" + (b.ghost ? " ghost" : ""); el.textContent = b.label;
            el.onclick = function () { overlay.hidden = true; if (b.fn) { b.fn(); } };
            holder.appendChild(el);
        });
        overlay.hidden = false; holder.firstChild.focus();
    }

    // Hand in
    function finish(how) {
        if (finished) { return; }
        return post("/api/canvas/submit", { pid: C.pid, boxes: boxes(), how: how }).then(function () {
            finished = true; location.href = C.doneUrl;
        });
    }
    submitBtn.addEventListener("click", function () {
        if (filled() < C.minFilled) {
            modal(T.confirm_title, T.need_more.replace("{n}", C.minFilled), [{ label: T.confirm_no }]); return;
        }
        modal(T.confirm_title, T.confirm_text, [
            { label: T.confirm_yes, fn: function () { finish("button"); } },
            { label: T.confirm_no, ghost: true }]);
    });

    // Timer (soft limit: at zero the slide is handed in as it is)
    var left = C.secondsLeft;
    function tick() {
        var m = Math.floor(left / 60), s = left % 60;
        timerEl.textContent = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
        timerEl.classList.toggle("low", left <= 60);
        if (left <= 0) {
            clearInterval(iv);
            modal(T.confirm_title, T.timeup, []);
            document.getElementById("modal-title").textContent = T.timeup.split(".")[0];
            finish("timeout").catch(function () { location.href = C.doneUrl; });
            return;
        }
        left -= 1;
    }
    var iv = setInterval(tick, 1000); tick();
    window.addEventListener("beforeunload", function () {
        if (dirty && !finished) {
            try { navigator.sendBeacon("/api/canvas", new Blob([JSON.stringify({ pid: C.pid, boxes: boxes() })], { type: "application/json" })); } catch (e) {}
        }
    });

    // AI co-founder panel
    if (C.ai) {
        var thread = document.getElementById("thread"), form = document.getElementById("chatform");
        var input = document.getElementById("chatinput"), send = document.getElementById("send"), busy = false;
        function scrollDown() { thread.scrollTop = thread.scrollHeight; }
        function bubble(role, text) {
            var m = document.createElement("div"); m.className = "msg " + role;
            var b = document.createElement("div"); b.className = "bubble"; b.textContent = text;
            m.appendChild(b); thread.appendChild(m); scrollDown(); return m;
        }
        function typing() {
            var m = document.createElement("div"); m.className = "msg assistant";
            m.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
            thread.appendChild(m); scrollDown(); return m;
        }
        function grow() { input.style.height = "auto"; input.style.height = Math.min(input.scrollHeight, 140) + "px"; }
        input.addEventListener("input", grow);
        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
        });
        scrollDown();
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            var text = input.value.trim();
            if (!text || busy || finished) { return; }
            busy = true; send.disabled = true;
            bubble("user", text); input.value = ""; grow();
            var wait = typing();
            post("/api/chat", { pid: C.pid, message: text, boxes: boxes() }).then(function (r) {
                wait.remove(); bubble("assistant", r.reply);
            }).catch(function (err) {
                wait.remove(); bubble("assistant", (err && err.error) || T.ai_error);
            }).then(function () { busy = false; send.disabled = false; input.focus(); });
        });
    }
})();
