import threading
import 

class TrashCleaner(threading.Thread):
    def __init__(self, db):
        Thread.__init__(self)
        self.cursor = db.cursor
        self.work = True

    def run(self):
        while self.work:

