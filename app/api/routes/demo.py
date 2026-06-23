from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.workflows.incident_workflow import analyze_incident

router = APIRouter()

DEMO_CLEARANCE_LEVEL = 5


class DemoAnalyzeRequest(BaseModel):
    query: str


@router.get("/demo", response_class=HTMLResponse)
def demo_page():
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Secure RAG Auditor Demo</title>
        <style>
          :root {
            --bg: #08111f;
            --panel: #0f1b2d;
            --panel-2: #142235;
            --text: #edf5ff;
            --muted: #9fb0c7;
            --line: #263a55;
            --accent: #36d1c4;
            --accent-2: #8be9df;
            --danger: #ff7a7a;
            --warn: #ffd166;
            --ok: #76e4a6;
            --shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
          }

          * { box-sizing: border-box; }

          body {
            margin: 0;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: radial-gradient(circle at 20% 0%, #132b43 0%, var(--bg) 34%, #050b14 100%);
            color: var(--text);
            line-height: 1.5;
          }

          .wrap {
            width: min(1120px, calc(100% - 32px));
            margin: 0 auto;
          }

          nav {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            padding: 22px 0;
          }

          nav a {
            color: var(--muted);
            font-weight: 700;
            text-decoration: none;
          }

          nav a:hover { color: var(--accent-2); }

          header {
            padding: 46px 0 28px;
          }

          h1 {
            margin: 0;
            font-size: clamp(38px, 7vw, 68px);
            line-height: 1;
            letter-spacing: 0;
          }

          .description {
            max-width: 760px;
            margin: 18px 0 0;
            color: var(--muted);
            font-size: 18px;
          }

          .demo-grid {
            display: grid;
            grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
            gap: 18px;
            padding: 24px 0 56px;
          }

          .guide-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 18px;
            margin: 8px 0 20px;
          }

          .panel {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(15, 27, 45, 0.92);
            box-shadow: var(--shadow);
          }

          .guide {
            padding: 22px;
          }

          .guide h2 {
            margin: 0 0 12px;
            font-size: 20px;
            letter-spacing: 0;
          }

          .guide ul {
            margin: 0;
            padding-left: 20px;
            color: var(--muted);
          }

          .input-panel {
            padding: 22px;
          }

          label {
            display: block;
            margin-bottom: 10px;
            color: var(--accent-2);
            font-size: 14px;
            font-weight: 800;
            text-transform: uppercase;
          }

          textarea {
            width: 100%;
            min-height: 128px;
            resize: vertical;
            padding: 14px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #07101e;
            color: var(--text);
            font: inherit;
          }

          .quick {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 10px;
            margin-top: 14px;
          }

          button {
            min-height: 42px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel-2);
            color: var(--text);
            font-weight: 800;
            cursor: pointer;
          }

          button:hover { border-color: var(--accent); }

          .analyze {
            width: 100%;
            margin-top: 16px;
            background: var(--accent);
            border-color: var(--accent);
            color: #031018;
          }

          .results {
            padding: 22px;
            min-height: 420px;
          }

          .state {
            color: var(--muted);
          }

          .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin-bottom: 14px;
          }

          .card {
            padding: 14px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #081322;
          }

          .card span {
            display: block;
            color: var(--muted);
            font-size: 13px;
            font-weight: 700;
          }

          .card strong {
            display: block;
            margin-top: 4px;
            color: var(--accent-2);
            font-size: 22px;
          }

          .section {
            margin-top: 16px;
            padding-top: 14px;
            border-top: 1px solid var(--line);
          }

          .section h2 {
            margin: 0 0 8px;
            font-size: 18px;
            letter-spacing: 0;
          }

          ul {
            margin: 0;
            padding-left: 20px;
            color: var(--muted);
          }

          pre {
            overflow-x: auto;
            padding: 12px;
            border-radius: 8px;
            background: #050b14;
            color: var(--muted);
          }

          @media (max-width: 860px) {
            .demo-grid { grid-template-columns: 1fr; }
          }
        </style>
      </head>
      <body>
        <div class="wrap">
          <nav>
            <a href="/">Home</a>
            <a href="/docs">Swagger Docs</a>
            <a href="https://github.com/suryaprakash737/Secure_Rag_Auditor">GitHub Repository</a>
          </nav>

          <header>
            <h1>Secure RAG Auditor Demo</h1>
            <p class="description">Interact with the AI-powered security analysis workflow using realistic security queries.</p>
          </header>

          <section class="guide-grid" aria-label="Demo guidance">
            <article class="panel guide">
              <h2>How to Use This Demo</h2>
              <ul>
                <li>Select a sample query or type your own.</li>
                <li>Click Analyze.</li>
                <li>The system checks for prompt injection.</li>
                <li>Retrieves relevant logs.</li>
                <li>Applies threat intelligence.</li>
                <li>Runs LangGraph incident workflow.</li>
                <li>Returns risk level, findings, recommendation, sources, and threat context.</li>
              </ul>
            </article>
            <article class="panel guide">
              <h2>Where This Is Used</h2>
              <ul>
                <li>SOC investigations.</li>
                <li>Failed login analysis.</li>
                <li>Malware triage.</li>
                <li>Unauthorized access investigation.</li>
                <li>Threat hunting.</li>
                <li>Security log summarization.</li>
                <li>Safe AI-assisted incident analysis.</li>
              </ul>
            </article>
          </section>

          <main class="demo-grid">
            <section class="panel input-panel">
              <label for="query">Security query</label>
              <textarea id="query" placeholder="show failed login attempts">show failed login attempts</textarea>
              <div class="quick">
                <button type="button" data-query="show failed login attempts">Failed Login Attempts</button>
                <button type="button" data-query="show malware detection events">Malware Detection</button>
                <button type="button" data-query="show unauthorized access attempts">Unauthorized Access</button>
                <button type="button" data-query="show suspicious network activity">Suspicious Network Activity</button>
              </div>
              <button class="analyze" id="analyze" type="button">Analyze</button>
            </section>

            <section class="panel results" id="results">
              <p class="state">Enter a security query and run the demo workflow.</p>
            </section>
          </main>
        </div>

        <script>
          const queryInput = document.getElementById("query");
          const results = document.getElementById("results");
          const analyze = document.getElementById("analyze");

          document.querySelectorAll("[data-query]").forEach((button) => {
            button.addEventListener("click", () => {
              queryInput.value = button.dataset.query;
              queryInput.focus();
            });
          });

          function escapeHtml(value) {
            return String(value ?? "")
              .replaceAll("&", "&amp;")
              .replaceAll("<", "&lt;")
              .replaceAll(">", "&gt;")
              .replaceAll('"', "&quot;")
              .replaceAll("'", "&#039;");
          }

          function listItems(items) {
            if (!items || items.length === 0) return "<p class='state'>None reported.</p>";
            return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
          }

          function renderResult(data) {
            const intel = data.threat_intel_findings || [];
            const sources = data.sources || [];
            results.innerHTML = `
              <div class="cards">
                <article class="card"><span>Risk Level</span><strong>${escapeHtml(data.risk_level)}</strong></article>
                <article class="card"><span>Log Count</span><strong>${escapeHtml(data.log_count)}</strong></article>
              </div>
              <div class="section">
                <h2>Key Findings</h2>
                ${listItems(data.key_findings)}
              </div>
              <div class="section">
                <h2>Recommendation</h2>
                <p class="state">${escapeHtml(data.recommendation)}</p>
              </div>
              <div class="section">
                <h2>Threat Intelligence Findings</h2>
                <pre>${escapeHtml(JSON.stringify(intel, null, 2))}</pre>
              </div>
              <div class="section">
                <h2>Sources</h2>
                <pre>${escapeHtml(JSON.stringify(sources, null, 2))}</pre>
              </div>
            `;
          }

          analyze.addEventListener("click", async () => {
            const query = queryInput.value.trim();
            if (!query) {
              results.innerHTML = "<p class='state'>Please enter a query.</p>";
              return;
            }

            analyze.disabled = true;
            results.innerHTML = "<p class='state'>Running secure analysis workflow...</p>";

            try {
              const response = await fetch("/demo/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query }),
              });
              const data = await response.json();
              if (!response.ok) throw new Error(data.detail || "Analysis failed");
              renderResult(data);
            } catch (error) {
              results.innerHTML = `<p class='state'>${escapeHtml(error.message)}</p>`;
            } finally {
              analyze.disabled = false;
            }
          });
        </script>
      </body>
    </html>
    """


@router.post("/demo/analyze")
def analyze_demo(request: DemoAnalyzeRequest):
    return analyze_incident(request.query, DEMO_CLEARANCE_LEVEL)
