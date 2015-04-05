import threading
import time
from crontab import CronTab

__author__ = 'Omry_Nachman'

def noop():
    return False


class RepeatingTask:
    def __init__(self, condition_handler, get_next_interval, kill_switch=noop):
        self.condition_handler = condition_handler
        self.get_next_interval = get_next_interval
        self.kill_switch = kill_switch
        self.on_kill = noop
        self.timer = threading.Timer(get_next_interval, self.execute)

    def execute(self):
        if not self.kill_switch():
            self.condition_handler.execute()
            self.timer = threading.Timer(self.get_next_interval, self.execute)
        else:
            self.on_kill()

    def cancel(self):
        self.timer.cancel()
        self.on_kill()


def timestamp():
    return "%s" % time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())


class Scheduler(threading.Thread):
    def __init__(self, name='default', log=None):
        print "hello"
        super(Scheduler, self).__init__(name = name)
        self.alive = True
        self.running_tasks = []
        self.last_id = 0
        if log:
            self.log = lambda x: log("[%s %s<Scheduler>] %s" % (timestamp(), self.name, x))
        else:
            self.log = lambda x: x
        log("%s<Scheduler> created" % name)

    def run(self):
        self.log("started")
        while self.alive:
            pass
        self.kill()
        self.log("terminated")

    def interval(self, condition_handler, interval, kill_switch=noop):
        self.log("Adding interval task: %s, every %d seconds" % (condition_handler.name, interval))
        return self._addTask(condition_handler, lambda x: interval, kill_switch)

    def cron(self, condition_handler, cron_str, kill_switch=noop):
        self.log("Adding cron task: %s, at %s" % (condition_handler.name, cron_str))
        return self._addTask(condition_handler, CronTab(cron_str).next, kill_switch)

    def kill(self):
        self.alive = False
        while len(self.running_tasks) > 0:
            self.log("cancelling %d tasks" % len(self.running_tasks))
            for task in self.running_tasks:
                task.cancel()
            time.sleep(0.001)

    def _addTask(self, condition_handler, get_next_interval, kill_switch):
        task = RepeatingTask(condition_handler, get_next_interval, kill_switch)
        task.on_kill = lambda: self.running_tasks.remove(task)
        self.running_tasks.append(task)
        return task
