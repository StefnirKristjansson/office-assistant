# Project Setup

## Setup on Windows

1. Install the latest version of Python on your local machine. For example, if you have Python 3.11 installed, you can place it in the directory `C:\python\py311`.

2. Create a virtual environment in this directory by typing:

    ```bash
    C:\python\py311\python -m venv venv
    ```

3. Activate the virtual environment. In the command line, type:

    ```bash
    venv\Scripts\activate
    ```

    In Visual Studio Code, if you have the Python extension installed, you should see a popup asking if you want to use the new virtual environment.

4. Install the required packages by typing:

    ```bash
    pip install -r requirements.txt
    ```

5. You should now be able to run the application using the `run.py` file.

**Note:** For non-Windows users, adjust the commands accordingly:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## How the project is structured

.
├── app                      # Main application package
│   ├── main.py              # Application entry point
│   ├── api                  # External API related code
│   ├── database             # Database related code and models
│   ├── models               # Models used in the application
│   ├── routes               # FastAPI routes
│   ├── security             # Security related code
│   ├── static               # Static files
│   ├── temp                 # Temporary files
│   ├── utils                # Utility functions
├── tests                    # Unit tests for application
├── requirements.txt         # Python requirements
├── run.py                   # Script for starting the application
├── README.md                # Project's README file
├── Dockerfile               # Dockerfile for building the image
├── .env                     # Environment variable definitions
└── htmlcov                  # Directory where coverage reports are stored


## Important Notes

- **DO NOT EDIT** existing classes in `models.py`. They do not automatically update in production. If you create a new class it will be created but old classes will **NOT** be updated.
- Do not work on the main branch, always create a branch from main and work on that. When it's ready, create a pull request to main. Direct pushes to main will be rejected.

When working with this application, you need to know:

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/)

## Working with Alembic for Database Migrations

Alembic is a database migration tool used with SQLAlchemy and SQLModel. It allows you to manage changes to your database schema over time.

### Running Migrations

To apply all pending migrations to your local database, navigate to the root directory of the project and run:

```bash
alembic upgrade head
```

This command will apply all pending migrations to your local database.

## Create a new migration by running:

When you make changes to your models (e.g., add a new column, modify a table), you need to create a new migration script. Alembic is already configured in the project, so you can generate a migration using:

```bash
alembic revision --autogenerate -m "Your message here"
```

This command will generate a new migration script based on the changes you made to your models.

## Apply the new migration by running:

After generating a new migration script, you need to apply it to your local database. To do this, run:

```bash
alembic upgrade head
```

This command will apply the new migration to your local database.

## downgrade a migration by running:

To downgrade a migration, you can run:

```bash
alembic downgrade -1
```

This command will revert the last migration applied to your local database.

## Working with the Repository

- Do not create a branch without any existing issues on GitHub. To fix an issue, create a branch from that issue and work on that.
- Start off by writing the tests and when that is done create a draft pull request.
- When the draft pull request is created work on the issue, when the code is ready make the draft pull request ready for review.

## Required Tests before Merging a Pull Request

- Pytest
- Pylint
- Coverage

### Running Tests

- **Pytest**: Run pytest by typing the following in the command line:

    ```bash
    pytest
    ```

- **Pylint**: Run pylint by typing the following in the command line:

    ```bash
    pylint /path
    ```

- **Coverage**: Run coverage by typing the following in the command line:

    ```bash
    pytest --cov-report term --cov=app tests/ --cov-report html
    ```

  Then the HTML report will be created in the `htmlcov` folder. Open the `index.html` file in the browser to see the report.

All Pytests need to pass before a pull request can be merged. 100% coverage is not needed but it is preferred. The test will fail if coverage is below 90%. Pylint needs to 100% pass before a pull request can be merged.

*Please update the README if you make any alterations that other developers need to be aware of.*
