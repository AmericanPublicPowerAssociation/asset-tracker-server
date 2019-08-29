# Asset Tracker

    sudo dnf -y install redis spatialite
    sudo systemctl start redis

    cd ~/Experiments/asset-tracker-server
    pip install --user -e .
    alembic -c development.ini revision --autogenerate -m 'Initialize database'
    alembic -c development.ini upgrade head

    cd ~/Experiments/asset-tracker-server
    pserve development.ini --reload

## Test

    pip install --user -e .[testing]
    py.test
