from app.modules.notification.models import Notification


def test_notification_model_declares_unread_payload_and_user_query_contract() -> None:
    columns = Notification.__table__.c
    indexes = {index.name for index in Notification.__table__.indexes}

    assert Notification.__tablename__ == "notifications"
    assert columns.user_id.nullable is False
    assert columns.notification_type.nullable is False
    assert columns.payload.nullable is False
    assert columns.is_read.nullable is False
    assert "ix_notifications_user_read_created_at" in indexes
    assert "ix_notifications_notification_type" in indexes
