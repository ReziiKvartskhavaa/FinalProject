from fp.tags import clean_emojis, map_tags_to_clusters


def test_clean_emojis_keeps_words():
    assert clean_emojis("🍕 pizza, dessert") == " pizza, dessert"


def test_map_tags_to_clusters_unknown():
    mapping = {"pizza": "fast food"}
    out = map_tags_to_clusters("pizza, sushi", mapping)
    assert out == ["fast food", "unknown"]
