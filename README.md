# Asset Tracker

    cd ~/Experiments/asset-tracker-server
    pip install --user --upgrade pipenv
    pipenv install --three -e .[testing]
    pipenv shell
    alembic -c development.ini revision --autogenerate -m 'Start app'
    alembic -c development.ini upgrade head
    py.test

    cd ~/Experiments/asset-tracker-server
    pipenv shell
    pserve development.ini
