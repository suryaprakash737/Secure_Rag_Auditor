from html import escape

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlmodel import Session, select

from app.api.dependencies.auth import require_role
from app.db.session import get_session
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.admin import AdminStatsResponse, AuditLogResponse

router = APIRouter(prefix="/admin")


def _count_audits(session: Session, *conditions) -> int:
    statement = select(func.count(AuditLog.id))
    for condition in conditions:
        statement = statement.where(condition)
    return session.exec(statement).one()


def _recent_audits(session: Session, limit: int) -> list[AuditLog]:
    statement = (
        select(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
    )
    return session.exec(statement).all()


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    current_user: User = Depends(require_role(["admin"])),
    session: Session = Depends(get_session),
):
    total_queries = _count_audits(session)
    blocked_queries = _count_audits(session, AuditLog.was_blocked == True)

    return AdminStatsResponse(
        total_queries=total_queries,
        blocked_queries=blocked_queries,
        allowed_queries=total_queries - blocked_queries,
        critical_queries=_count_audits(session, AuditLog.risk_level == "Critical"),
        high_queries=_count_audits(session, AuditLog.risk_level == "High"),
        medium_queries=_count_audits(session, AuditLog.risk_level == "Medium"),
        low_queries=_count_audits(session, AuditLog.risk_level == "Low"),
    )


@router.get("/recent-audits", response_model=list[AuditLogResponse])
def get_recent_audits(
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(require_role(["admin"])),
    session: Session = Depends(get_session),
):
    return _recent_audits(session, limit)


@router.get("/dashboard", response_class=HTMLResponse)
def get_admin_dashboard(
    current_user: User = Depends(require_role(["admin"])),
    session: Session = Depends(get_session),
):
    total_queries = _count_audits(session)
    blocked_queries = _count_audits(session, AuditLog.was_blocked == True)
    stats = {
        "Total Queries": total_queries,
        "Blocked Queries": blocked_queries,
        "Allowed Queries": total_queries - blocked_queries,
        "Critical": _count_audits(session, AuditLog.risk_level == "Critical"),
        "High": _count_audits(session, AuditLog.risk_level == "High"),
        "Medium": _count_audits(session, AuditLog.risk_level == "Medium"),
        "Low": _count_audits(session, AuditLog.risk_level == "Low"),
    }
    recent_audits = _recent_audits(session, 10)

    stat_cards = "".join(
        f"<article class='stat'><span>{escape(label)}</span><strong>{value}</strong></article>"
        for label, value in stats.items()
    )
    audit_rows = "".join(
        "<tr>"
        f"<td>{escape(str(audit.timestamp))}</td>"
        f"<td>{escape(audit.query_text)}</td>"
        f"<td>{audit.user_clearance}</td>"
        f"<td>{escape(audit.risk_level)}</td>"
        f"<td>{audit.log_count}</td>"
        f"<td>{'Yes' if audit.was_blocked else 'No'}</td>"
        "</tr>"
        for audit in recent_audits
    )
    if not audit_rows:
        audit_rows = "<tr><td colspan='6'>No audit records found.</td></tr>"

    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Secure RAG Auditor Admin Dashboard</title>
        <style>
          :root {{
            --bg: #f5f7fb;
            --panel: #ffffff;
            --ink: #172033;
            --muted: #5d6b82;
            --line: #d9e1ec;
            --accent: #116466;
            --shadow: 0 14px 34px rgba(23, 32, 51, 0.08);
          }}
          * {{ box-sizing: border-box; }}
          body {{
            margin: 0;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: var(--bg);
            color: var(--ink);
          }}
          main {{
            width: min(1180px, calc(100% - 32px));
            margin: 0 auto;
            padding: 42px 0;
          }}
          h1 {{ margin: 0; font-size: 38px; letter-spacing: 0; }}
          .sub {{ margin: 8px 0 26px; color: var(--muted); }}
          .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 14px;
          }}
          .stat {{
            padding: 18px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            box-shadow: var(--shadow);
          }}
          .stat span {{ display: block; color: var(--muted); font-weight: 700; }}
          .stat strong {{ display: block; margin-top: 8px; color: var(--accent); font-size: 34px; }}
          .table-wrap {{
            margin-top: 28px;
            overflow-x: auto;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            box-shadow: var(--shadow);
          }}
          table {{ width: 100%; border-collapse: collapse; min-width: 850px; }}
          th, td {{ padding: 13px 14px; border-bottom: 1px solid var(--line); text-align: left; }}
          th {{ color: var(--muted); font-size: 13px; text-transform: uppercase; }}
          td {{ font-size: 14px; }}
          tr:last-child td {{ border-bottom: 0; }}
        </style>
      </head>
      <body>
        <main>
          <h1>Admin Audit Dashboard</h1>
          <p class="sub">Read-only operational view of PostgreSQL audit activity.</p>
          <section class="stats" aria-label="Audit statistics">{stat_cards}</section>
          <section class="table-wrap" aria-label="Recent audit records">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Query</th>
                  <th>Clearance</th>
                  <th>Risk</th>
                  <th>Logs</th>
                  <th>Blocked</th>
                </tr>
              </thead>
              <tbody>{audit_rows}</tbody>
            </table>
          </section>
        </main>
      </body>
    </html>
    """
