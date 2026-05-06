from app.database.engine import get_database_url, init_db
from app.database.seed import seed_database


def bootstrap_database(seed: bool = False, reset: bool = False) -> str:
    init_db(drop_existing=reset)
    if seed:
        seed_database(force_reset=False)
    return get_database_url()


if __name__ == "__main__":
    database_url = bootstrap_database(seed=True)
    print(f"Base de datos inicializada en {database_url}")
