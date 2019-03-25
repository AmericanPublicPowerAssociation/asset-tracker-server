# Asset Tracker

    pip install --user --upgrade pipenv
    cd asset-tracker-server
    pipenv install --three -e .[testing]
    alembic -c development.ini revision --autogenerate -m Start
    alembic -c development.ini upgrade head
    initialize_asset_tracker_db development.ini
    pytest
    pserve development.ini
