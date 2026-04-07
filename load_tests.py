from locust import HttpUser, between, task


class MovieNightUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def docs(self) -> None:
        self.client.get("/docs")
