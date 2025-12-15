"""
Background tasks for the application.

This module handles scheduled background tasks like session cleanup.
Uses APScheduler for reliable task scheduling.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.session_manager import session_manager
import logging
import os

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = BackgroundScheduler()

# Configuration from environment or defaults
CLEANUP_INTERVAL_MINUTES = int(os.getenv("CLEANUP_INTERVAL_MINUTES", "10"))


def cleanup_sessions_task():
    """
    Background task to clean up expired sessions.
    Runs periodically to prevent memory leaks.
    """
    try:
        removed = session_manager.cleanup_all_expired_sessions()
        
        if removed > 0:
            logger.info(f"[SESSION CLEANUP] Removed {removed} expired session(s)")
        
        # Log session statistics
        active_count = session_manager.get_active_sessions_count()
        logger.debug(f"[SESSION STATS] Active sessions: {active_count}")
        
    except Exception as e:
        logger.error(f"[SESSION CLEANUP ERROR] {str(e)}", exc_info=True)


def start_background_tasks():
    """
    Start all background tasks.
    Should be called once on application startup.
    """
    # Schedule session cleanup
    scheduler.add_job(
        func=cleanup_sessions_task,
        trigger=IntervalTrigger(minutes=CLEANUP_INTERVAL_MINUTES),
        id='cleanup_sessions',
        name='Clean up expired sessions',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info(f"[SCHEDULER] Background tasks started (cleanup every {CLEANUP_INTERVAL_MINUTES} minutes)")


def stop_background_tasks():
    """
    Stop all background tasks.
    Should be called on application shutdown.
    """
    try:
        scheduler.shutdown(wait=False)
        logger.info("[SCHEDULER] Background tasks stopped")
    except Exception as e:
        logger.error(f"[SCHEDULER ERROR] Failed to stop scheduler: {str(e)}")

