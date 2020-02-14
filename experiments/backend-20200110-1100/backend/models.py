class Asset(Base):
    deleted = Column('deleted', Boolean(name='deleted_bool'), default=False)
    json_required_field = [('name', str), ('type_code', str)]
