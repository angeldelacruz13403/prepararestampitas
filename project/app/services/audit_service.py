from flask import request

from app.extensions import db
from app.models import AdminLog, SessionLog


def log_session(user_id: int) -> None:
    db.session.add(
        SessionLog(
            user_id=user_id,
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
            user_agent=(request.user_agent.string if request.user_agent else None),
        )
    )
    db.session.commit()


def log_admin_action(user_id: int, action: str, detail: str | None = None) -> None:
    db.session.add(AdminLog(user_id=user_id, action=action, detail=detail))
    db.session.commit()
