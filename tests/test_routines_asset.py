from asset_tracker.exceptions import DataValidationError
from asset_tracker.routines.asset import (
    get_asset_attributes, get_asset_connections, get_asset_dictionary_by_id,
    get_asset_feature_collection)
from pytest import raises


def test_get_asset_dictionary_by_id():
    with raises(DataValidationError):
        get_asset_dictionary_by_id({'assetById': 1})
    with raises(DataValidationError):
        get_asset_dictionary_by_id({'assetById': [1]})
    with raises(DataValidationError):
        get_asset_dictionary_by_id({'assetById': {'a': 1}})
    with raises(DataValidationError):
        get_asset_dictionary_by_id({'assetById': {'a': [1]}})
    get_asset_dictionary_by_id({})
    get_asset_dictionary_by_id({'assetById': {'a': {}}})
    get_asset_dictionary_by_id({'assetById': {'a': {'name': 'x'}}})


def test_get_asset_feature_collection():
    with raises(DataValidationError):
        get_asset_feature_collection({'assetsGeoJson': 1})
    with raises(DataValidationError):
        get_asset_feature_collection({'assetsGeoJson': {'features': 1}})
    get_asset_feature_collection({'assetsGeoJson': {'features': []}})


def test_get_asset_attributes():
    with raises(DataValidationError):
        get_asset_attributes({'attributes': 1})
    get_asset_attributes({})
    get_asset_attributes({'attributes': {}})


def test_get_asset_connections():
    with raises(DataValidationError):
        get_asset_connections({'connections': 1})
    with raises(DataValidationError):
        get_asset_connections({'connections': {'a': {}}})
    with raises(DataValidationError):
        get_asset_connections({'connections': {1: 1}})
    with raises(DataValidationError):
        get_asset_connections({'connections': {1: {'attributes': 1}}})
    get_asset_connections({})
    get_asset_connections({'connections': {}})
    get_asset_connections({'connections': {1: {}}})
    get_asset_connections({'connections': {1: {'attributes': {}}}})
