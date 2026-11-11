(function () {
    "use strict";
    var V = window.VIDEOS || {}, T = window.VT || {}, DUR = 3400;
    if (!Object.keys(V).length) { return; }
    var wrap = document.createElement("div"); wrap.className = "vid-wrap"; wrap.hidden = true;
    wrap.innerHTML = '<div class="vid" id="vid" role="dialog" aria-modal="true" aria-label="Mini-video">' +
        '<div class="vid-icon" id="vid-icon"></div><p class="vid-cap" id="vid-cap"></p>' +
        '<div class="vid-end"><button type="button" id="vid-again" class="ghost"></button><button type="button" id="vid-done"></button></div>' +
        '<div class="vid-dots" id="vid-dots"></div>' +
        '<div class="vid-bar"><button type="button" id="vid-pp"></button><button type="button" id="vid-skip"></button></div></div>';
    document.body.appendChild(wrap);
    var $ = function (id) { return document.getElementById(id); };
    var vid = $("vid"), cur = null, idx = 0, timer = null, paused = false, startedAt = 0, left = DUR, seen = {};
    $("vid-again").textContent = T.v_replay || "Watch again"; $("vid-done").textContent = T.v_close || "Close"; $("vid-skip").textContent = T.v_skip || "Skip";
    function log(type, detail) {
        try { fetch("/api/event", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pid: window.VPID, page: "video", type: type, detail: detail }) }).catch(function () {}); } catch (e) {}
    }
    function show(i) {
        var clip = V[cur]; idx = i; clearTimeout(timer);
        if (i >= clip.scenes.length) { vid.classList.add("ended"); vid.classList.remove("paused"); paused = false; log("video_end", cur); markDots(clip.scenes.length); $("vid-pp").style.visibility = "hidden"; return; }
        vid.classList.remove("ended"); $("vid-pp").style.visibility = "visible";
        var sc = clip.scenes[i], icon = $("vid-icon"), cap = $("vid-cap");
        icon.style.animation = "none"; cap.style.animation = "none"; void icon.offsetWidth; icon.style.animation = ""; cap.style.animation = "";
        icon.textContent = sc[0]; cap.textContent = sc[1];
        markDots(i); left = DUR; startedAt = Date.now();
        if (!paused) { timer = setTimeout(function () { show(i + 1); }, left); }
    }
    function markDots(i) {
        var d = $("vid-dots"); d.innerHTML = "";
        V[cur].scenes.forEach(function (_, k) {
            var el = document.createElement("i"), b = document.createElement("b"); el.appendChild(b);
            if (k < i) { el.className = "done"; } else if (k === i) { el.className = "cur"; el.style.setProperty("--d", DUR + "ms"); }
            d.appendChild(el);
        });
    }
    function setPaused(p) {
        if (vid.classList.contains("ended")) { return; }
        paused = p; vid.classList.toggle("paused", p); $("vid-pp").textContent = p ? (T.v_play || "Play") : (T.v_pause || "Pause");
        clearTimeout(timer);
        if (p) { left = Math.max(300, left - (Date.now() - startedAt)); }
        else { startedAt = Date.now(); var i = idx; timer = setTimeout(function () { show(i + 1); }, left); }
    }
    function open(clip) {
        if (!V[clip]) { return; }
        cur = clip; paused = false; vid.classList.remove("paused", "ended"); vid.style.setProperty("--vc", V[clip].color);
        $("vid-pp").textContent = T.v_pause || "Pause"; wrap.hidden = false; seen[clip] = true; log("video_play", clip); show(0); $("vid-done").focus();
    }
    function close() {
        clearTimeout(timer); var ended = vid.classList.contains("ended"); wrap.hidden = true;
        if (!ended) { log("video_skip", cur + ":" + idx); }
        var b = document.querySelector('.vid-open[data-clip="' + cur + '"]'); if (b) { b.classList.remove("new"); b.focus(); }
    }
    $("vid-skip").addEventListener("click", function (e) { e.stopPropagation(); if (idx + 1 >= V[cur].scenes.length) { close(); } else { show(idx + 1); } });
    $("vid-pp").addEventListener("click", function (e) { e.stopPropagation(); setPaused(!paused); });
    $("vid-again").addEventListener("click", function (e) { e.stopPropagation(); open(cur); });
    $("vid-done").addEventListener("click", function (e) { e.stopPropagation(); close(); });
    vid.addEventListener("click", function () { setPaused(!paused); });
    wrap.addEventListener("click", function (e) { if (e.target === wrap) { close(); } });
    document.addEventListener("keydown", function (e) { if (!wrap.hidden && e.key === "Escape") { close(); } });

    Array.prototype.forEach.call(document.querySelectorAll(".vid-open"), function (b) {
        b.addEventListener("click", function () { open(b.getAttribute("data-clip")); });
    });
    // on the canvas page the box clip follows the box being edited
    var boxBtn = document.getElementById("vid-box");
    window.addEventListener("boxchange", function (e) {
        if (!boxBtn) { return; }
        var key = e.detail; boxBtn.setAttribute("data-clip", key);
        boxBtn.hidden = !V[key]; boxBtn.classList.toggle("new", !!V[key] && !seen[key]);
    });
    if (document.getElementById("vid-intro")) { document.getElementById("vid-intro").classList.add("new"); }
})();
