from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from models import Asset, Busbar, ElectricalConnection


engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()


asset1 = Asset(id='asset1')
asset2 = Asset(id='asset2')
busbar = Busbar(id='busbar')
electrical_connection1 = ElectricalConnection(
    asset_id=asset1.id,
    busbar_id=busbar.id,
    busbar_node=1)
electrical_connection2 = ElectricalConnection(
    asset_id=asset2.id,
    busbar_id=busbar.id,
    busbar_node=1)


db.add(asset1)
db.add(asset2)
db.add(busbar)
db.add(electrical_connection1)
db.add(electrical_connection2)
db.commit()


electrical_connections = db.query(
    ElectricalConnection
).filter_by(
    busbar_id=busbar.id,
    busbar_node=1)
for electrical_connection in electrical_connections:
    print(electrical_connection)
