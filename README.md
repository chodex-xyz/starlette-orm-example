# The example of using [Starlette](https://github.com/encode/starlette) with new [async ORM](https://github.com/encode/orm) 

1. Install dependencies
    ```
    pip3 install -r requirements.txt
    ```
1. Setup .env

1. create the database
    ```python
    import sqlalchemy
    from app import database, metadata
    
    engine = sqlalchemy.create_engine(str(database.url))
    metadata.create_all(engine)
    ```
1. Run in a development mode with auto reload
    ```
    uvicorn app:app --reload
    ```
