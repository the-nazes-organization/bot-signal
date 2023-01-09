from app.bot.data_utils import enrich_user_data_with_db_name


def test_enrich_user_data(user_oriented_data, user_map_storage):
    filled_data_dict = user_oriented_data["filled"].dict()
    enriched_data_dict = enrich_user_data_with_db_name(
        user_oriented_data["empty"],
        user_map_storage
    ).dict()
    assert filled_data_dict == enriched_data_dict

def test_enrich_user_data_empty_db(user_oriented_data, object_storage):
    empty_data_dict = user_oriented_data["empty"].dict()
    enriched_data_dict = enrich_user_data_with_db_name(
        user_oriented_data["empty"],
        object_storage
    ).dict()
    assert empty_data_dict == enriched_data_dict
