class VulnerableAsset(Base):
    __tablename__ = 'vulnerable_asset'
    id = Column(String, primary_key=True)
    asset_id = Column(String, ForeignKey('asset.id'), nullable=False)
    vulnerability_description = Column(String, nullable=False)
    vulnerability_date_published = Column(DateTime, nullable=False)
    vulnerability_score = Column(Float)
    UniqueConstraint('asset_id', 'id')
