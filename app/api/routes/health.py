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
            color-scheme: light;
            --bg: #f6f8fb;
            --surface: #ffffff;
            --text: #172033;
            --muted: #5d6b82;
            --border: #d9e1ec;
            --accent: #116466;
            --accent-dark: #0b4648;
            --shadow: 0 12px 32px rgba(23, 32, 51, 0.08);
          }

          * {
            box-sizing: border-box;
          }

          body {
            margin: 0;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
          }

          main {
            width: min(1120px, calc(100% - 32px));
            margin: 0 auto;
            padding: 64px 0;
          }

          .hero {
            display: grid;
            gap: 24px;
            padding: 48px 0 40px;
          }

          h1 {
            margin: 0;
            font-size: clamp(40px, 7vw, 72px);
            line-height: 1;
            letter-spacing: 0;
          }

          .subtitle {
            margin: 0;
            max-width: 780px;
            color: var(--accent-dark);
            font-size: 24px;
            font-weight: 700;
          }

          .description {
            margin: 0;
            max-width: 760px;
            color: var(--muted);
            font-size: 18px;
          }

          .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
          }

          .button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 44px;
            padding: 0 18px;
            border: 1px solid var(--accent);
            border-radius: 8px;
            color: #ffffff;
            background: var(--accent);
            font-weight: 700;
            text-decoration: none;
          }

          .button.secondary {
            color: var(--accent-dark);
            background: transparent;
          }

          .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 16px;
            margin-top: 24px;
          }

          .feature {
            min-height: 120px;
            padding: 20px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            box-shadow: var(--shadow);
          }

          .feature h2 {
            margin: 0 0 8px;
            font-size: 18px;
            letter-spacing: 0;
          }

          .feature p {
            margin: 0;
            color: var(--muted);
            font-size: 14px;
          }
        </style>
      </head>
      <body>
        <main>
          <section class="hero">
            <h1>Secure RAG Auditor</h1>
            <p class="subtitle">AI-Powered Security Log Analysis Platform</p>
            <p class="description">
              Analyze security logs with clearance-aware retrieval, prompt injection defenses,
              audit logging, threat intelligence enrichment, and workflow-ready incident reasoning.
            </p>
            <div class="actions">
              <a class="button" href="/docs">View API Docs</a>
              <a class="button secondary" href="https://github.com/suryaprakash737/Secure_Rag_Auditor">GitHub Repo</a>
            </div>
          </section>

          <section class="features" aria-label="Platform features">
            <article class="feature"><h2>JWT Authentication</h2><p>Token-based access for authenticated users.</p></article>
            <article class="feature"><h2>RBAC</h2><p>Admin-only controls for protected operations.</p></article>
            <article class="feature"><h2>Prompt Injection Defense</h2><p>Pattern-based blocking before retrieval and analysis.</p></article>
            <article class="feature"><h2>PostgreSQL Audit Logging</h2><p>Persistent query audit records for reporting.</p></article>
            <article class="feature"><h2>Threat Intelligence</h2><p>Deterministic enrichment for detected indicators.</p></article>
            <article class="feature"><h2>LangGraph Workflow</h2><p>Multi-step incident reasoning pipeline foundation.</p></article>
            <article class="feature"><h2>Docker + CI/CD</h2><p>Containerized runtime with GitHub Actions validation.</p></article>
            <article class="feature"><h2>Pytest Coverage</h2><p>Focused tests for security and workflow foundations.</p></article>
          </section>
        </main>
      </body>
    </html>
    """


@router.get("/health")
def health():
    return {"status": "The Secure Vault is Online"}
