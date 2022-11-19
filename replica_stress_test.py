from locust import HttpUser, TaskSet, task, between
import random
import time

origin = "http://proj4-repl1.5700.network/"
port = 8080


def getList():
    fd = open("pageviews.csv", "r")
    views = fd.read()
    ls = views.split("\n")[2:]
    ls = [_.split(",") for _ in ls]
    queries = []
    for item in ls:
        item = item[-1]
        queries.append("/" + item.replace(" ", "_"))
    return queries
        

class users(HttpUser):
    
    wait_time = between(1, 5)
    
    def on_start(self):
        self.paths = getList()
        self.client.get("")
        return super().on_start()
    
    @task(10)
    def stressTest(self):
        self.client.get(url=self.paths[random.randint(0, len(self.paths)-1)])


if __name__ == "__main__":
    getList()