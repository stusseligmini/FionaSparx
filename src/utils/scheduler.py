import schedule
import logging
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger(__name__)

class ContentScheduler:
    """Avansert scheduler for innholdspublisering"""
    
    def __init__(self, config):
        self.config = config
        self.timezone = pytz.timezone(config.get("timezone", "Europe/Oslo"))
        self.post_times = config.get("post_times", ["12:00"])
        self.auto_run = config.get("auto_run", True)
        self.setup_scheduler()
        logger.info("⏰ Content Scheduler initialisert")
    
    def setup_scheduler(self):
        """Sett opp scheduling jobs"""
        if not self.auto_run:
            logger.info("📅 Automatisk scheduling deaktivert")
            return
        
        # Sett opp daglige poster
        for post_time in self.post_times:
            schedule.every().day.at(post_time).do(self._scheduled_content_generation)
            logger.info(f"📅 Planlagt innholdsgenerering kl. {post_time}")
        
        # Sett opp ukentlig analyse
        schedule.every().monday.at("09:00").do(self._weekly_analysis)
        
        # Sett opp månedlig cleanup
        schedule.every().month.do(self._monthly_cleanup)
        
        # Sett opp daglig reset av tellere ved midnatt
        schedule.every().day.at("00:00").do(self._daily_reset)
    
    def _scheduled_content_generation(self):
        """Planlagt innholdsgenerering"""
        logger.info("⏰ Utfører planlagt innholdsgenerering")
        # Denne vil bli kalt av hovedklassen
        return "generate_content"
    
    def _weekly_analysis(self):
        """Ukentlig analyse"""
        logger.info("📊 Utfører ukentlig analyse")
        return "weekly_analysis"
    
    def _monthly_cleanup(self):
        """Månedlig cleanup"""
        logger.info("🧹 Utfører månedlig cleanup")
        return "monthly_cleanup"
    
    def _daily_reset(self):
        """Daglig reset av tellere"""
        logger.info("🔄 Utfører daglig reset")
        return "daily_reset"
    
    def get_next_scheduled_time(self):
        """Hent neste planlagte tid"""
        next_run = schedule.next_run()
        if next_run:
            return next_run.astimezone(self.timezone)
        return None
    
    def get_schedule_info(self):
        """Hent informasjon om scheduling"""
        jobs = []
        for job in schedule.jobs:
            jobs.append({
                "job": str(job.job_func),
                "next_run": job.next_run,
                "interval": job.interval,
                "unit": job.unit
            })
        
        return {
            "total_jobs": len(schedule.jobs),
            "next_run": self.get_next_scheduled_time(),
            "timezone": str(self.timezone),
            "auto_run": self.auto_run,
            "jobs": jobs
        }
