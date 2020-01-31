class Asset(Base):
    deleted = Column('deleted', Boolean(name='deleted_bool'), default=False)
    json_required_field = [('name', str), ('type_code', str)]

    def get_json_d(self):
        d = dict(self.attributes or {}, **{
            'id': self.id,
            'name': self.name,
            'type_code': self.type_code,
            'busByIndex': {_.id: _.get_json_d() for _ in self.connections}
        })
        return d

    @classmethod
    def make_asset_from_json(cls, json):
        for column, d_type in cls.json_required_field:
            if not isinstance(column, d_type):
                return None
        # returns one asset
        pass

    @classmethod
    def update_from_json_list(cls, old_asset, updated_asset):
        # returns updated data
        pass


class Connection(Base):

    def get_json_d(self):
        return dict(self.attributes or {}, **{
            'busId': self.asset_id,
            'attributes': self.attributes
        })


class TaskStatus(enum.Enum):
    Cancelled = -100
    New = 0
    Pending = 50
    Done = 100


class Task(Base):
    __tablename__ = 'task'
    id = Column(String, primary_key=True)
    asset_id = Column(String, ForeignKey('asset.id'))
    asset = relationship('Asset', backref='tasks')
    reference_uri = Column(String)
    name = Column(Unicode)
    status = Column(Enum(TaskStatus), default=TaskStatus.New)
    creation_user_id = Column(String)
    assignment_user_id = Column(String)

    def get_json_d(self):
        return {
            'id': self.id,
            'assetId': self.asset_id,
            'assetName': self.asset.name,
            'referenceUri': self.reference_uri,
            'name': self.name,
            'status': self.status.value,
            'creationUserId': self.creation_user_id,
            'assignmentUserId': self.assignment_user_id,
        }
