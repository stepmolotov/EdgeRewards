from injector import Injector, inject, provider

class Database:
    def __init__(self, host, port) -> None
        self.host = host
        self.port = port

class UserRepository:
    def __init__(self, database: Database):
        self.database = database

@provider
def provide_database() -> Database:
    host = "localhost"
    port = 5432
    return Database(host, port)

@inject
def use_user_repository(user_repository: UserRepository) -> None
    print(user_repository.database.host)
    print(user_repository.database.port)

def main() -> None:
    injector = Injector()
    user_repository = injector.get(UserRepository)
    use_user_repository(user_repository)

if __name__ == "__main__":
    main()
