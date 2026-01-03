
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from services.notification_service import notification_service

router = APIRouter()

class NotificationRequest(BaseModel):
    message: str
    level: str = "info"

@router.post("/telegram")
async def send_telegram_notification(request: NotificationRequest, background_tasks: BackgroundTasks):
    """
    Send a Telegram notification via n8n.
    Background task is used to avoid blocking.
    """
    # Run in background to reply quickly to client
    background_tasks.add_task(notification_service.send_telegram_message, request.message, request.level)
    return {"status": "queued", "message": "Notification scheduled"}
