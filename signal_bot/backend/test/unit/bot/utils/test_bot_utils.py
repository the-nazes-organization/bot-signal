from signal_bot.backend.bot.data_utils import enrich_user_data_with_db_name

def test_enrich_user_data(mocker, user_oriented_data, user_map_storage):
    mocker.patch(
        "signal_bot.backend.bot.data_utils.get_number_map_db",
        return_value=user_map_storage
    )

    filled_data_dict = user_oriented_data["filled"].dict()
    enriched_data_dict = enrich_user_data_with_db_name(
        user_oriented_data["empty"]
    ).dict()
    assert filled_data_dict == enriched_data_dict


def test_enrich_user_data_empty_db(mocker, user_oriented_data, object_storage):
    mocker.patch(
        "signal_bot.backend.bot.data_utils.get_number_map_db",
        return_value=object_storage
    )

    empty_data_dict = user_oriented_data["empty"].dict()
    enriched_data_dict = enrich_user_data_with_db_name(
        user_oriented_data["empty"]
    ).dict()
    assert empty_data_dict == enriched_data_dict
