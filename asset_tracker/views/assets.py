from pyramid.view import view_config


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='POST',
)
def add_assets_json():
    pass


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='GET',
)
def see_assets_json():
    pass


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='GET',
)
def see_asset_json():
    pass


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='PATCH',
)
def change_asset_json():
    pass


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='DELETE',
)
def drop_asset_json():
    pass
