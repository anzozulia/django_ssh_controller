from threading import Thread

from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def start_scheduler():
        from scheduler import run_scheduler
        Thread(target=run_scheduler).start()

    def ready(self):

        def start_scheduler():
            from app.scheduler import run_scheduler
            Thread(target=run_scheduler).start()

        start_scheduler()
        
        # from app.monitor.metrics import SystemMetrics
        # from app.monitor.sysdrivers import Local, SSH

        # driver = SSH(
        #     host="88.198.201.77",
        #     username="support",
        #     key="/tmp/88.198.201.77",
        # )

        # metrics = SystemMetrics(driver)