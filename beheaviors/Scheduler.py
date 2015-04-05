from crontab import CronTab
import threading
from time import sleep

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


class Scheduler(threading.Thread):
    def __init__(self, min_interval=0.1):
        self.min_interval = min_interval
        self.alive = True
        self.running_tasks = []
        self.last_id = 0

    def run(self):
        while self.alive:
            pass

        while len(self.running_tasks) > 0:
            for task in self.running_tasks:
                task.cancel()
            sleep(0.001)

    def interval(self, condition_handler, interval, kill_switch=noop):
        return self._addTask(condition_handler, lambda x: interval, kill_switch)

    def cron(self, condition_handler, cron_str, kill_switch=noop):
        return self._addTask(condition_handler, CronTab(cron_str).next, kill_switch)

    def kill(self):
        self.alive = False
        for task in self.running_tasks:
            task.timer.cancel()

    def _addTask(self, condition_handler, get_next_interval, kill_switch):
        task = RepeatingTask(condition_handler, get_next_interval, kill_switch)
        task.on_kill = lambda x: self.running_tasks.remove(task)
        self.running_tasks.append(task)
        return task
