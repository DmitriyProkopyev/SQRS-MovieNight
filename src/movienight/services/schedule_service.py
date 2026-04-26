from movienight.schemas.schedule import ScheduleResponse


class ScheduleService:
    def __init__(self, db) -> None:
        self.db = db

    def get_week_schedule(self) -> ScheduleResponse:
        data = self.db.get_schedule()
        return ScheduleResponse.model_validate(data)