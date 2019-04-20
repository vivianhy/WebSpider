from multiprocessing import Process
from crawler import Getter
from tester import Tester
import time

TESTER_CYCLE = 60
GETTER_CYCLE = 600
TESTER_ENABLED = True
GETTER_ENABLED = True

class Scheduler(object):
    def __init__(self):
        self.getter = Getter()
        self.tester = Tester()

    # 定时获取代理
    def scheduler_getter(self, cycle=GETTER_CYCLE):
        while True:
            self.getter.run()
            time.sleep(cycle)

    # 定时测试代理
    def schedule_tester(self, cycle=TESTER_CYCLE):
        while True:
            self.tester.run()
            time.sleep(cycle)

    def run(self):
        print('代理池开始运行！')
        if GETTER_ENABLED:
            getter_process = Process(target = self.scheduler_getter)
            getter_process.start()
        
        if TESTER_ENABLED:
            tester_process = Process(target = self.schedule_tester)
            tester_process.start()

if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.run()