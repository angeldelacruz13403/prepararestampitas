from flask import request

from app.extensions import db
from app.models import AdminLog, SessionLog
from app.utils.security import get_client_ip


def log_session(user_id: int) -> None:
    db.session.add(
        SessionLog(
            user_id=user_id,
            ip_address=get_client_ip(),
            user_agent=(request.user_agent.string if request.user_agent else None),
        )
    )
    db.session.commit()


def log_admin_action(user_id: int, action: str, detail: str | None = None) -> None:
    db.session.add(AdminLog(user_id=user_id, action=action, detail=detail))
    db.session.commit()
