
src="https://jsdelivr.net"

async function postJSON(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data),
  });
  return res.json();
}

document.getElementById("btn-document").addEventListener("click", async () => {
  const prompt = document.getElementById("doc-prompt").value;
  const r = await postJSON("/api/document", {prompt});
  document.getElementById("doc-result").innerText = r.result;
});

document.getElementById("btn-table").addEventListener("click", async () => {
  const prompt = document.getElementById("table-prompt").value;
  const r = await postJSON("/api/table", {prompt});
  document.getElementById("table-result").innerText = r.result;
});

document.getElementById("btn-gmail").addEventListener("click", async () => {
  const g_task = document.getElementById("gmail-task").value;
  const prompt = ""; // optional prompt field; you can adapt if needed
  const extra = {};
  if (g_task === "full") extra.num = parseInt(document.getElementById("gmail-num").value || "1", 10);
  if (g_task === "email") {
    extra.to = document.getElementById("gmail-to").value;
    extra.subject = document.getElementById("gmail-subject").value;
    extra.instructions = document.getElementById("gmail-instr").value;
  }
  const r = await postJSON("/api/gmail", {prompt, g_task, extra});
  document.getElementById("gmail-result").innerText = r.result;
});

document.getElementById("btn-search-prompt").addEventListener("click", async () => {
  const prompt = document.getElementById("search-prompt").value;
  const r = await postJSON("/api/search_prompt", {prompt});
  
  document.getElementById("search-result").innerHTML = marked.parse(r.result);
});
