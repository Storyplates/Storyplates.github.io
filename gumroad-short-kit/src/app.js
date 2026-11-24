(function () {
  const drop = window.DAILY_DROP || {};
  const topics = window.TOPICS || [];
  const byId = (id) => document.getElementById(id);
  const safe = (value) => String(value || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  byId("drop-title").textContent = drop.topic_title || "Today's idea";
  byId("drop-hook").textContent = drop.hook || "Start with a real question your viewer might ask.";
  byId("drop-narration").textContent = drop.narration || "Choose one useful action, explain why it helps, and invite the viewer to try it.";
  byId("drop-video-title").textContent = drop.title || "A useful phone-tip Short";
  byId("drop-description").textContent = drop.description || "Use the official source linked with this idea, then describe your own demonstration.";
  byId("drop-source").href = drop.source_url || "https://support.google.com/android/";
  const scenes = Array.isArray(drop.scenes) ? drop.scenes : [];
  byId("drop-scenes").innerHTML = scenes.map((scene) => `<li>${safe(scene)}</li>`).join("");
  const tags = Array.isArray(drop.tags) ? drop.tags : [];
  byId("drop-tags").innerHTML = tags.map((tag) => `<span class="tag">${safe(tag)}</span>`).join("");

  const grid = byId("topic-grid");
  function renderTopics(query) {
    const words = String(query || "").trim().toLowerCase();
    const selected = topics.filter((topic) => !words || `${topic.title} ${topic.id}`.toLowerCase().includes(words));
    grid.innerHTML = selected.map((topic) => `<article class="topic-card"><h3>${safe(topic.title)}</h3><p>Build one short, practical explanation from Google's official Android help page.</p><div class="topic-bottom"><a class="topic-link" href="${safe(topic.url)}" target="_blank" rel="noreferrer">Open source ↗</a><button class="use-topic" data-topic="${safe(topic.id)}">Use idea</button></div></article>`).join("") || "<p>No ideas match that search yet.</p>";
    grid.querySelectorAll("[data-topic]").forEach((button) => button.addEventListener("click", () => {
      const topic = topics.find((item) => item.id === button.dataset.topic);
      if (!topic) return;
      byId("idea").value = topic.title;
      byId("source-url").value = topic.url;
      byId("builder-section").scrollIntoView({ behavior: "smooth", block: "center" });
    }));
  }
  renderTopics("");
  byId("search").addEventListener("input", (event) => renderTopics(event.target.value));

  byId("make-prompt").addEventListener("click", () => {
    const idea = byId("idea").value.trim();
    const audience = byId("audience").value.trim() || "a beginner phone user";
    const source = byId("source-url").value.trim();
    if (!idea || !source) {
      toast("Add a topic and its official source link first.");
      return;
    }
    const prompt = `Write one original 25- to 40-second vertical video script for ${audience}.\n\nTopic: ${idea}\nOfficial source: ${source}\n\nUse only claims supported by the source. Start with one natural question, explain one practical action in plain language, add four short on-screen beats, and end with a friendly invitation to try it and comment. Say that menu names can vary by phone/version when relevant. Return a concise title, voiceover, four captions, a two-sentence description with the source link, and three to five relevant search tags. Avoid copied phrasing, copyrighted footage, generic viral claims, or unrelated trending tags.`;
    byId("prompt-output").textContent = prompt;
    byId("prompt-output-wrap").hidden = false;
    byId("prompt-output-wrap").scrollIntoView({ behavior: "smooth", block: "nearest" });
  });

  const toastNode = byId("toast");
  function toast(message) {
    toastNode.textContent = message;
    toastNode.classList.add("show");
    setTimeout(() => toastNode.classList.remove("show"), 1800);
  }
  function copyText(kind) {
    if (kind === "narration") return drop.narration || "";
    if (kind === "tags") return tags.join(", ");
    if (kind === "prompt") return byId("prompt-output").textContent;
    return "";
  }
  document.querySelectorAll("[data-copy]").forEach((button) => button.addEventListener("click", async () => {
    const text = copyText(button.dataset.copy);
    if (!text) return;
    try { await navigator.clipboard.writeText(text); toast("Copied to clipboard."); }
    catch (_) { toast("Select the text and copy it."); }
  }));
})();
