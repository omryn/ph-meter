import threading
import time
from crontab import CronTab

__author__ = 'Omry_Nachman'


def noop():
    return False


class RepeatingTask(object):
    def __init__(self, id, condition_handler, get_next_interval, kill_switch=noop, log=lambda x: x):
        self.condition_handler = condition_handler
        self.get_next_interval = get_next_interval
        self.kill_switch = kill_switch
        self.on_kill = noop
        self.log = lambda x: log("Task[%d](%s): %s" % (id, condition_handler.name, x))
        self.timer = None
        self.log("Task created")

    def _set_next_execution(self):
        interval = self.get_next_interval()
        self.log("Next execution in %.3f seconds" % interval)
        self.timer = threading.Timer(interval, self.execute)
        self.timer.start()

    def start(self):
        self.log("Started")
        self._set_next_execution()

    def execute(self):
        if not self.kill_switch():
            self.log("Executing task")
            result = self.condition_handler.execute()
            self.log("Execution results: %s" % str(result))
            self._set_next_execution()
        else:
            self.log("kill_switch returned True, killing task")
            self.on_kill()

    def cancel(self):
        self.log("Task cancelled")
        if self.timer:
            self.timer.cancel()
        self.on_kill()
        self.timer.join(1)


def timestamp():
    return "%s" % time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())


class Scheduler(threading.Thread):
    def __init__(self, name='default', log=None):
        super(Scheduler, self).__init__(name=name)
        self.alive = False
        self.running_tasks = []
        self.pending_tasks = []
        self.last_task_id = 0
        if log:
            self.log = lambda x: log("[%s %s<Scheduler>] %s" % (timestamp(), self.name, x))
        else:
            self.log = lambda x: None
        self.log("Created")

    def run(self):
        self.log("Started")
        self.alive = True
        while self.alive:
            for task in self.pending_tasks:
                self.pending_tasks.remove(task)
                task.start()
                self.running_tasks.append(task)
        self.kill()
        self.log("Terminated")

    def interval(self, condition_handler, interval, kill_switch=noop):
        self.log("Adding interval task: %s, every %d seconds" % (condition_handler.name, interval))
        return self._addTask(condition_handler, lambda: interval, kill_switch)

    def cron(self, condition_handler, cron_str, kill_switch=noop):
        self.log("Adding cron task: %s, at %s" % (condition_handler.name, cron_str))
        return self._addTask(condition_handler, CronTab(cron_str).next, kill_switch)

    def kill(self):
        self.alive = False
        while len(self.running_tasks) > 0:
            self.log("cancelling %d tasks" % len(self.running_tasks))
            for task in self.pending_tasks:
                task.cancel()
            for task in self.running_tasks:
                task.cancel()
            time.sleep(0.001)

    def _addTask(self, condition_handler, get_next_interval, kill_switch):
        task = RepeatingTask(self.last_task_id, condition_handler, get_next_interval, kill_switch, self.log)
        self.last_task_id += 1
        task.on_kill = lambda: self.running_tasks.remove(task)
        self.pending_tasks.append(task)
        return task
