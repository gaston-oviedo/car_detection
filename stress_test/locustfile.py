from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):

    @task(1)
    def index(self):
        self.client.get("/")

    @task(3)
    def predict(self):
        files = [("file", ("dog.jpeg", open("dog.jpeg", "rb"), "image/jpeg"))]
        headers = {}
        payload = {}

        self.client.post("/predict", headers=headers, data=payload, files=files)


class APIUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
