# Asset Tracker

Please see the Asset Tracker [README](http://github.com/AmericanPublicPowerAssociation/asset-tracker) for full installation instructions.

## Install

    virtualenv -p $(which python3) \
        ~/.virtualenvs/asset-tracker-server
    source ~/.virtualenvs/asset-tracker-server/bin/activate
    cd ~/Projects/asset-tracker-server
    pip install -e .

## Prototype

    source ~/.virtualenvs/asset-tracker-server/bin/activate
    cd ~/Projects/asset-tracker-server
    invisibleroads initialize development.ini
    pserve development.ini

## Deploy

    mkdir ~/Experiments/asset-tracker-server
    cp ~/Projects/asset-tracker-server/production.ini \
        ~/Experiments/asset-tracker-server

    source ~/.virtualenvs/asset-tracker-server/bin/activate
    cd ~/Experiments/asset-tracker-server
    invisibleroads initialize production.ini
    alembic -c production.ini revision --autogenerate -m 'Start'
    alembic -c production.ini upgrade head
    pserve production.ini
