import schedule
import pytz
import traceback
import telebot

from time import sleep
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.db.models import F

from app.models import Server, ServerCheck, Settings
from app.monitor.metrics import SystemMetrics

def check_server(server, bot=None):
    ssh_client = server.get_ssh_client()
    metrics = SystemMetrics(ssh_client)
    metrics = metrics.save(server)

    if metrics.status == 'success':
        for alert in server.alerts.all():
            altered, status = alert.status_check(metrics)
            if altered and status:
                if Settings.load().tg_alerts and bot:
                    bot.send_message(Settings.load().tg_chat_id, alert.text, parse_mode='markdown')
    else:
        if metrics.new_error:
            if Settings.load().tg_alerts and bot:
                bot.send_message(Settings.load().tg_chat_id, metrics.error_text, parse_mode='markdown')

def check_servers():
    bot = telebot.TeleBot(Settings.load().tg_bot_token, threaded=False)

    # Server.objects.all().update(check_interval=3)
    for server in filter(lambda server: server.pending_for_check, Server.objects.filter(active=True)):
        check_server(server, bot)
        

def run_scheduler():
    schedule.every(10).seconds.do(check_servers)

    while True:
        try:
            schedule.run_pending()
        except Exception as ex:
            traceback.print_exc()
        sleep(1)