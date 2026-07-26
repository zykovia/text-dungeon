from text_dungeon.gold import gold_for_kill


def test_gold_for_kill_regular_monster():
    assert gold_for_kill("giant rat", "Dungeon Lord", "Dungeon Emperor") == 2


def test_gold_for_kill_boss():
    assert gold_for_kill("Dungeon Lord", "Dungeon Lord", "Dungeon Emperor") == 5


def test_gold_for_kill_super_boss():
    assert gold_for_kill("Dungeon Emperor", "Dungeon Lord", "Dungeon Emperor") == 5


def test_gold_for_kill_with_no_super_boss_name():
    assert gold_for_kill("giant rat", "Dungeon Lord") == 2
    assert gold_for_kill("Dungeon Lord", "Dungeon Lord") == 5
