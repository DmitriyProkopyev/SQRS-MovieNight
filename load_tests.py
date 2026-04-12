from locust import HttpUser, between, task
import random


class MovieNightUser(HttpUser):
    """Тестирование производительности Voting и Scheduling логики"""
    wait_time = between(1, 3)

    def on_start(self):
        self.user_id = f"perf_user_{random.randint(1000, 999999)}"
        self.movie_ids = []

    @task(3)
    def view_movies(self):
        """GET /api/movies - получение списка фильмов"""
        with self.client.get("/api/movies", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self.movie_ids = [m.get("id") for m in data if m.get("id")]
                except:
                    pass
            elif response.status_code not in [404]:
                response.failure(f"Movies failed: {response.status_code}")

    @task(2)
    def view_screenings(self):
        """GET /api/screenings - проверка Scheduling"""
        with self.client.get("/api/screenings", catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure(f"Screenings failed: {response.status_code}")

    @task(2)
    def cast_vote(self):
        """POST /api/votes - проверка Core Voting Logic"""
        if not self.movie_ids:
            return
        
        movie_id = random.choice(self.movie_ids)
        payload = {"user_id": self.user_id, "movie_id": movie_id}
        
        with self.client.post("/api/votes", json=payload, catch_response=True) as response:
            if response.status_code not in [200, 201, 409, 404]:
                response.failure(f"Vote failed: {response.status_code}")

    @task(1)
    def docs(self):
        """GET /docs - базовый health check"""
        self.client.get("/docs")