# Asset Tracker

    cd asset-tracker-server
    pip install --user --upgrade pipenv
    pipenv install --three -e .[testing]
    pipenv shell
    alembic -c development.ini revision --autogenerate -m Start
    alembic -c development.ini upgrade head
    initialize_asset_tracker_db development.ini
    pytest

    cd asset-tracker-server
    pipenv shell
    pserve development.ini
