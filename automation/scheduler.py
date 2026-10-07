"""Runs the refresh pipeline on a recurring schedule using APScheduler."""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

from apscheduler.schedulers.blocking import BlockingScheduler

import config
from automation.refresh import run_refresh
from utils.helper import get_logger

logger = get_logger("scheduler")


def scheduled_job():
    try:
        result = run_refresh()
        logger.info("Scheduled refresh result: %s", result)
    except Exception as exc:
        logger.error("Scheduled refresh failed: %s", exc)


def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(
        scheduled_job,
        "interval",
        minutes=config.SCHEDULER_INTERVAL_MINUTES,
        next_run_time=None,
    )
    logger.info(
        "Scheduler started | interval=%d minutes", config.SCHEDULER_INTERVAL_MINUTES
    )
    scheduled_job()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    start_scheduler()
