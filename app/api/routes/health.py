from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Secure RAG Auditor</title>
        <style>
          :root {
            --bg: #f5f7fb;
            --ink: #111827;
            --muted: #5b6475;
            --line: #d9e1ec;
            --panel: #ffffff;
            --panel-2: #eef7f7;
            --accent: #116466;
            --accent-2: #0b4648;
            --warn: #b45309;
            --shadow: 0 16px 40px rgba(17, 24, 39, 0.08);
          }

          * { box-sizing: border-box; }

          body {
            margin: 0;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: var(--bg);
            color: var(--ink);
            line-height: 1.5;
          }

          a { color: inherit; }

          .wrap {
            width: min(1180px, calc(100% - 32px));
            margin: 0 auto;
          }

          .hero {
            padding: 72px 0 44px;
            border-bottom: 1px solid var(--line);
            background: linear-gradient(180deg, #ffffff 0%, #f5f7fb 100%);
          }

          .eyebrow {
            margin: 0 0 14px;
            color: var(--accent-2);
            font-size: 14px;
            font-weight: 800;
            text-transform: uppercase;
          }

          h1 {
            margin: 0;
            max-width: 920px;
            font-size: clamp(42px, 7vw, 76px);
            line-height: 1;
            letter-spacing: 0;
          }

          .subtitle {
            margin: 18px 0 0;
            max-width: 760px;
            color: var(--accent-2);
            font-size: 24px;
            font-weight: 800;
          }

          .description {
            margin: 18px 0 0;
            max-width: 780px;
            color: var(--muted);
            font-size: 18px;
          }

          .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 28px;
          }

          .button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 44px;
            padding: 0 18px;
            border: 1px solid var(--accent);
            border-radius: 8px;
            background: var(--accent);
            color: #ffffff;
            font-weight: 800;
            text-decoration: none;
          }

          .button.secondary {
            background: #ffffff;
            color: var(--accent-2);
          }

          .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 14px;
            margin-top: 40px;
          }

          .metric, .feature, .tech {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            box-shadow: var(--shadow);
          }

          .metric {
            padding: 18px;
          }

          .metric strong {
            display: block;
            color: var(--accent-2);
            font-size: 26px;
          }

          .metric span {
            color: var(--muted);
            font-weight: 700;
          }

          section {
            padding: 48px 0;
          }

          .section-title {
            margin: 0 0 18px;
            font-size: 30px;
            letter-spacing: 0;
          }

          .section-copy {
            max-width: 760px;
            margin: 0 0 24px;
            color: var(--muted);
          }

          .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
          }

          .feature {
            min-height: 128px;
            padding: 20px;
          }

          .feature h3, .tech h3 {
            margin: 0 0 8px;
            font-size: 18px;
            letter-spacing: 0;
          }

          .feature p, .tech p {
            margin: 0;
            color: var(--muted);
            font-size: 14px;
          }

          .flow {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 12px;
          }

          .flow-step {
            min-height: 82px;
            padding: 16px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel-2);
            font-weight: 800;
          }

          .diagram {
            width: 100%;
            margin-top: 20px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: var(--shadow);
          }

          .stack {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
          }

          .tech {
            padding: 16px;
          }

          footer {
            padding: 28px 0 42px;
            color: var(--muted);
            border-top: 1px solid var(--line);
          }
        </style>
      </head>
      <body>
        <header class="hero">
          <div class="wrap">
            <p class="eyebrow">Secure AI engineering portfolio project</p>
            <h1>Secure RAG Auditor</h1>
            <p class="subtitle">AI-Powered Security Log Analysis Platform</p>
            <p class="description">
              A production-style FastAPI platform for secure security-log analysis with JWT authentication,
              RBAC, prompt injection defense, clearance-aware RAG retrieval, threat intelligence enrichment,
              LangGraph incident workflow orchestration, and PostgreSQL auditability.
            </p>
            <div class="actions">
              <a class="button" href="/demo">Try Interactive Demo</a>
              <a class="button" href="/docs">View API Docs</a>
              <a class="button secondary" href="https://github.com/suryaprakash737/Secure_Rag_Auditor">GitHub Repo</a>
            </div>
            <div class="metrics" aria-label="Project metrics">
              <div class="metric"><strong>23+</strong><span>Automated Tests</span></div>
              <div class="metric"><strong>JWT + RBAC</strong><span>Authenticated authorization</span></div>
              <div class="metric"><strong>PostgreSQL</strong><span>Audit Trail</span></div>
              <div class="metric"><strong>LangGraph</strong><span>Incident Workflow</span></div>
            </div>
          </div>
        </header>

        <main>
          <section>
            <div class="wrap">
              <h2 class="section-title">Security Platform Capabilities</h2>
              <p class="section-copy">Built to show secure AI architecture, defensive controls, and production-minded engineering practices in one cohesive backend system.</p>
              <div class="features">
                <article class="feature"><h3>JWT Authentication</h3><p>Token-based identity for users and protected operations.</p></article>
                <article class="feature"><h3>RBAC</h3><p>Admin-only ingestion and reporting through reusable authorization dependencies.</p></article>
                <article class="feature"><h3>Prompt Injection Defense</h3><p>Malicious prompt patterns are blocked before retrieval or LLM analysis.</p></article>
                <article class="feature"><h3>PostgreSQL Audit Logging</h3><p>Every search outcome is persisted for operational reporting.</p></article>
                <article class="feature"><h3>Threat Intelligence</h3><p>Detected indicators are enriched with deterministic local intelligence.</p></article>
                <article class="feature"><h3>LangGraph Workflow</h3><p>Incident analysis is modeled as a multi-step reasoning pipeline.</p></article>
                <article class="feature"><h3>Docker + CI/CD</h3><p>Docker Compose runtime and GitHub Actions validation are included.</p></article>
                <article class="feature"><h3>Pytest Coverage</h3><p>Focused tests cover core security and workflow behavior.</p></article>
              </div>
            </div>
          </section>

          <section>
            <div class="wrap">
              <h2 class="section-title">Architecture Flow</h2>
              <div class="flow" aria-label="Architecture flow">
                <div class="flow-step">User Query</div>
                <div class="flow-step">JWT Authentication</div>
                <div class="flow-step">Prompt Injection Defense</div>
                <div class="flow-step">Clearance-Aware Retrieval</div>
                <div class="flow-step">Threat Intelligence Enrichment</div>
                <div class="flow-step">LangGraph Incident Workflow</div>
                <div class="flow-step">Groq LLM Analysis</div>
                <div class="flow-step">PostgreSQL Audit Logging</div>
              </div>
              <img class="diagram" src="/static/architecture.svg" alt="Secure RAG Auditor architecture diagram">
            </div>
          </section>

          <section>
            <div class="wrap">
              <h2 class="section-title">Technology Stack</h2>
              <div class="stack">
                <article class="tech"><h3>FastAPI</h3><p>API framework</p></article>
                <article class="tech"><h3>PostgreSQL</h3><p>Audit storage</p></article>
                <article class="tech"><h3>SQLModel</h3><p>ORM layer</p></article>
                <article class="tech"><h3>ChromaDB</h3><p>Vector retrieval</p></article>
                <article class="tech"><h3>Groq</h3><p>Llama 3.1 analysis</p></article>
                <article class="tech"><h3>LangGraph</h3><p>Workflow orchestration</p></article>
                <article class="tech"><h3>Docker</h3><p>Container runtime</p></article>
                <article class="tech"><h3>GitHub Actions</h3><p>CI validation</p></article>
              </div>
            </div>
          </section>
        </main>

        <footer>
          <div class="wrap">Built with FastAPI, PostgreSQL, ChromaDB, LangGraph, Docker, and Groq Llama 3.1</div>
        </footer>
      </body>
    </html>
    """


@router.get("/health")
def health():
    return {"status": "The Secure Vault is Online"}
