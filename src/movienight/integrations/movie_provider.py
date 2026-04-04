class MovieProvider:
    """Placeholder adapter for future external movie API integration."""

    def search(self, query: str) -> list[dict]:
        return [
            {
                "title": query,
                "year": None,
                "source": "stub",
            }
        ]
