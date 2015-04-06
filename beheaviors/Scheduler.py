import threading
import time
from crontab import CronTab

__author__ = 'Omry_Nachman'


def noop(*arg):
    return False


class RepeatingTask(object):
    def __init__(self, id, condition_handler, get_next_interval, kill_switch=noop, log=noop):
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

    def schedule(self, cron_or_interval, condition_handler, kill_switch=noop):
        try:
            schedule = float(cron_or_interval)
            self.log("Adding interval task: %s, every %d seconds" % (condition_handler.name, interval))
            return self._add_task(condition_handler, lambda: interval, kill_switch)
        except ValueError:
            self.log("Adding cron task: %s, at %s" % (condition_handler.name, cron_or_interval))
            return self._add_task(condition_handler, CronTab(cron_or_interval).next, kill_switch)

    def kill(self):
        self.alive = False
        while len(self.running_tasks) > 0:
            self.log("Cancelling %d tasks" % len(self.running_tasks))
            for task in self.pending_tasks:
                task.cancel()
            for task in self.running_tasks:
                task.cancel()
            time.sleep(0.001)

    def _remove_task(self, taks):
        self.pending_tasks.remove(task)
        self.running_tasks.remove(task)

    def _add_task(self, condition_handler, get_next_interval, kill_switch):
        task = RepeatingTask(self.last_task_id, condition_handler, get_next_interval, kill_switch, self.log)
        self.last_task_id += 1
        task.on_kill = lambda: self._remove_task(task)
        self.pending_tasks.append(task)
        return task


class SchedulerWithConfig(Scheduler):
    def __init__(self, name='default', log=None):
        super(SchedulerWithConfig, self).__init__(name, log)

    def add_schedule(self, schedule_list):
        for schedule, behavior in schedule_list:
            self.schedule(schedule, behavior)

    def load_config_module(self, module):
        conf = __import__(module)
        self.add_schedule(conf.schedule)