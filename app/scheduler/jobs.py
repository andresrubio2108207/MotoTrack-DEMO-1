from __future__ import annotations

from datetime import datetime

from app.services.alert_service import evaluate_alerts


def run_alert_scan(reference_date: datetime | None = None):
    return evaluate_alerts(reference_date=reference_date)
