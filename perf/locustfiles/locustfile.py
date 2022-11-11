from locust import HttpUser, task

class ApiUser(HttpUser):

    @task
    def health(self):
        self.client.get("/api/v1/health/")