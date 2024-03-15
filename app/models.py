from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import localtime, now

from app.monitor.types import TimeSpan, ByteSize

from app.monitor.sysdrivers import SSH

CHECK_INTERVALS = {
    3: _('3 seconds (DEBUG)'),
    60: _('1 minute'),
    300: _('5 minutes'),
    600: _('10 minutes'),
    1800: _('30 minutes'),
    3600: _('1 hour'),
    7200: _('2 hours'),
    14400: _('4 hours'),
    28800: _('8 hours'),
    43200: _('12 hours'),
    86400: _('24 hours'),
}

STATUS_CHOICES = {
    'success': _('Success'),
    'ssh_error': _('SSH Error'),
    'ping_error': _('Ping Error'),
}

METRICS = {
    'disk_used': _('Disk utilization (GB)'),
    'disk_available': _('Disk available (GB)'),
    'disk_percent': _('Disk utilization percent'),
    'load_1m': _('1 min load average'),
    'load_5m': _('5 min load average'),
    'load_15m': _('15 min load average'),
    'mem_free': _('Free memory (MB)'),
    'mem_available': _('Available memory (MB)'),
    'mem_used': _('Used memory (MB)'),
    'mem_cached': _('Cached memory (MB)'),
    'mem_percent': _('Memory utilization percent'),
    'swap_total': _('Total swap (MB)'),
    'swap_free': _('Free swap (MB)'),
    'swap_percent': _('Swap utilization percent'),
    'uptime': _('Uptime (s)'),
    'idle': _('Idle time (s)'),
}

CONDITION = {
    'gt': _('Greater than'),
    'gte': _('Greater than/equal'),
    'lt': _('Less than'),
    'lte': _('Less than/equal'),
    'eq': _('Equal'),
}

CONDITION_SYMBOLS = {
    'gt': '>',
    'gte': '≥',
    'lt': '<',
    'lte': '≤',
    'eq': '=',
}

TYPE = {
    'warning': _('Warning'),
    'critical': _('Critical'),
}

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls.objects.create()

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass


class Server(models.Model):
    name = models.CharField(max_length=64, null=True, blank=True)
    hostname = models.CharField(max_length=64)
    user = models.CharField(max_length=64)
    port = models.IntegerField(default=22)
    ssh_key = models.FileField(upload_to='ssh_keys', null=True, blank=True)
    last_check = models.DateTimeField(null=True)
    check_interval = models.IntegerField(default=5 * 60, choices=CHECK_INTERVALS)
    active = models.BooleanField(default=True)

    def get_ssh_client(self):
        return SSH (
            host=self.hostname,
            username=self.user,
            port=self.port,
            key=self.ssh_key.path
        )
    
    @property
    def live_metrics(self):
        return self.servercheck_set.order_by('-date').first()
    
    @property
    def pending_for_check(self):
        return not self.last_check or (now() - localtime(self.last_check)).seconds > self.check_interval

    @property
    def system_style(self):
        alerts = AlertSettings.objects.filter(server=self, metric__icontains='load', status=True)
        if alerts:
            return 'danger' if alerts.filter(type='critical').exists() else 'warning' 
        return 'success'
    
    @property
    def disk_style(self):
        alerts = AlertSettings.objects.filter(server=self, metric__icontains='disk', status=True)
        if alerts:
            return 'danger' if alerts.filter(type='critical').exists() else 'warning'
        return 'success'
    
    @property
    def memory_style(self):
        alerts = AlertSettings.objects.filter(server=self, metric__icontains='mem', status=True)
        if alerts:
            return 'danger' if alerts.filter(type='critical').exists() else 'warning'
        return 'success'
    
    @property
    def swap_style(self):
        alerts = AlertSettings.objects.filter(server=self, metric__icontains='swap', status=True)
        if alerts:
            return 'danger' if alerts.filter(type='critical').exists() else 'warning'
        return 'success'
    
    @property
    def status(self):
        if self.live_metrics.status != 'success':
            return 'critical'
        alerts = AlertSettings.objects.filter(server=self, status=True)
        if alerts.filter(type='critical').exists():
            return 'critical'
        elif alerts.filter(type='warning').exists():
            return 'warning'
        return 'ok'


    def __str__(self):
        return self.name if self.name else self.hostname
    

class ServerCheck(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES)
    
    disk_size = models.BigIntegerField(null=True)
    disk_used = models.BigIntegerField(null=True)
    disk_available = models.BigIntegerField(null=True)
    disk_percent = models.IntegerField(null=True)

    load_1m = models.FloatField(null=True)
    load_5m = models.FloatField(null=True)
    load_15m = models.FloatField(null=True)

    mem_total = models.BigIntegerField(null=True)
    mem_free = models.BigIntegerField(null=True)
    mem_available = models.BigIntegerField(null=True)
    mem_used = models.BigIntegerField(null=True)
    mem_cached = models.BigIntegerField(null=True)

    swap_total = models.BigIntegerField(null=True)
    swap_free = models.BigIntegerField(null=True)

    uptime = models.IntegerField(null=True)
    idle = models.IntegerField(null=True)
    
    @property
    def load_1m_int(self):
        return int(self.load_1m * 100)
    
    @property
    def load_5m_int(self):
        return int(self.load_5m * 100)
    
    @property
    def load_15m_int(self):
        return int(self.load_15m * 100)
    
    @property
    def bytesize_disk_size(self):
        return ByteSize(self.disk_size)
    
    @property
    def bytesize_disk_used(self):
        return ByteSize(self.disk_used)
    
    @property
    def bytesize_disk_available(self):
        return ByteSize(self.disk_available)
    
    @property
    def bytesize_mem_total(self):
        return ByteSize(self.mem_total)
    
    @property
    def bytesize_mem_free(self):
        return ByteSize(self.mem_free)
    
    @property
    def bytesize_mem_available(self):
        return ByteSize(self.mem_available)
    
    @property
    def bytesize_mem_used(self):
        return ByteSize(self.mem_used)
    
    @property
    def bytesize_mem_cached(self):
        return ByteSize(self.mem_cached)
    
    @property
    def bytesize_swap_total(self):
        return ByteSize(self.swap_total)
    
    @property
    def bytesize_swap_free(self):
        return ByteSize(self.swap_free)
    
    @property
    def mem_percent(self):
        return int((self.mem_total - self.mem_available) / self.mem_total * 100)
    
    @property
    def swap_percent(self):
        if self.swap_total:
            return int((self.swap_total - self.swap_free) / self.swap_total * 100)
        return 0
    
    @property
    def timespan_uptime(self):
        return TimeSpan(self.uptime)
    
    @property
    def timespan_idle(self):
        return TimeSpan(self.idle)
    
    @property
    def new_error(self):
        last_check = self.server.servercheck_set.exclude(pk=self.pk).order_by('-date').first()
        if last_check:
            return last_check.status != self.status
        return True

    @property
    def error_text(self):
        icon = '🔴'
        text = f"{icon} **{self.server}** {icon}\n"
        if self.status == 'ssh_error':
            text += "SSH connection failed"
        elif self.status == 'ping_error':
            text += "Host not responding"
        return text

    def save(self, *args, **kwargs):
        self.server.last_check = now()
        self.server.save(update_fields=['last_check'])
        super(ServerCheck, self).save(*args, **kwargs)


    
class AlertSettings(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    metric = models.CharField(max_length=64, choices=METRICS)
    condition = models.CharField(max_length=64, choices=CONDITION)
    value = models.FloatField()
    type = models.CharField(max_length=64, choices=TYPE)
    status = models.BooleanField(default=False)

    def metric_text(self):
        return METRICS[self.metric]
    
    def condition_text(self):
        return CONDITION[self.condition]
    
    def type_text(self):
        return TYPE[self.type]
    
    def value_text(self):
        if self.value.is_integer():
            return int(self.value)
        elif round(self.value, 2) == self.value:
            return round(self.value, 2)
        else:
            return self.value
        
    @property
    def value_multiplyer(self):
        if ("mem" in self.metric or "swap" in self.metric) and not "percent" in self.metric:
            return 1024 * 1024
        elif "disk" in self.metric and not "percent" in self.metric:
            return 1024 * 1024 * 1024
        return 1
        
    def check_condition(self, metrics):
        metric = getattr(metrics, self.metric)
        if self.condition == 'gt':
            return metric > self.value * self.value_multiplyer
        elif self.condition == 'gte':
            return metric >= self.value * self.value_multiplyer
        elif self.condition == 'lt':
            return metric < self.value * self.value_multiplyer
        elif self.condition == 'lte':
            return metric <= self.value * self.value_multiplyer
        elif self.condition == 'eq':
            return metric == self.value * self.value_multiplyer
        return False
    
    def status_check(self, metrics):
        current_status = self.status
        new_status = self.check_condition(metrics)
        self.status = new_status
        self.save()
        return current_status != new_status, new_status
    
    @property
    def metric_text_split(self):
        parts = METRICS[self.metric].split("(", 1)
        metric = parts[0].strip()
        unit = parts[1].rstrip(")").strip() if len(parts) > 1 else ""
        return metric, unit
    
    @property
    def text(self):
        icon = '🔴' if self.type == 'critical' else '🟡'
        text = f"{icon} **{self.server}** {icon}\n"
        metric, unit = self.metric_text_split
        text += f"{metric} {CONDITION_SYMBOLS[self.condition]} {self.value_text()} {unit}"
        return text


class Settings(SingletonModel):
    tg_bot_token = models.CharField(max_length=256, null=True, blank=True)
    tg_chat_id = models.CharField(max_length=256, null=True, blank=True)
    tg_alerts = models.BooleanField(default=True)