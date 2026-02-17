(function () {
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (!toggle || !nav) return;

  function setOpen(open) {
    nav.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  toggle.addEventListener("click", function () {
    setOpen(!nav.classList.contains("open"));
  });

  nav.addEventListener("click", function (e) {
    const link = e.target.closest("a");
    if (link) setOpen(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });
})();

/* Latest blog posts (Updates page only) */
(function () {
  const list = document.getElementById("blog-feed");
  if (!list) return;

  const FEED_URL = "https://valentineowan.wordpress.com/feed/";
  const MAX_POSTS = 6;

  function stripHtml(html) {
    const div = document.createElement("div");
    div.innerHTML = html || "";
    return (div.textContent || div.innerText || "").trim();
  }

  function escapeHtml(str) {
    return String(str)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function formatDate(d) {
    const date = new Date(d);
    if (Number.isNaN(date.getTime())) return "";
    return date.toLocaleDateString("en-GB", { day: "2-digit", month: "long", year: "numeric" });
  }

  function setFallback(message) {
    list.innerHTML = "";
    const li = document.createElement("li");
    li.className = "muted";
    li.textContent = message || "Recent posts could not load in this browser. Use the blog link above.";
    list.appendChild(li);
  }

  // RSS-to-JSON proxy to avoid CORS blocks on static sites like GitHub Pages
  const api = "https://api.rss2json.com/v1/api.json?rss_url=" + encodeURIComponent(FEED_URL);

  fetch(api, { method: "GET" })
    .then(function (r) {
      if (!r.ok) throw new Error("Feed request failed");
      return r.json();
    })
    .then(function (data) {
      const items = Array.isArray(data.items) ? data.items.slice(0, MAX_POSTS) : [];
      if (!items.length) {
        setFallback("No posts found yet.");
        return;
      }

      list.innerHTML = "";
      items.forEach(function (item) {
        const title = item.title || "Post";
        const link = item.link || "https://valentineowan.wordpress.com/";
        const dateText = formatDate(item.pubDate || item.publishedDate);
        const excerptRaw = stripHtml(item.description || item.content || "");
        const excerpt = excerptRaw.length > 180 ? excerptRaw.slice(0, 180) + "…" : excerptRaw;

        const li = document.createElement("li");
        li.innerHTML =
          '<div><strong><a class="text-link" href="' + escapeHtml(link) + '" target="_blank" rel="noopener">' +
          escapeHtml(title) +
          "</a></strong></div>" +
          (dateText ? '<div class="note">' + escapeHtml(dateText) + "</div>" : "") +
          (excerpt ? '<div class="muted mt-6">' + escapeHtml(excerpt) + "</div>" : "");

        list.appendChild(li);
      });
    })
    .catch(function () {
      setFallback();
    });
})();