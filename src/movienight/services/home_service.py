from movienight.schemas.home import HomePageResponse


class HomeService:
    def __init__(self, db) -> None:
        self.db = db

    def get_home_page(
        self,
        current_user,
        mine_only: bool = False,
    ) -> HomePageResponse:
        data = self.db.get_home(
            current_user_id=current_user.id,
            mine_only=mine_only,
        )
        return HomePageResponse.model_validate(data)