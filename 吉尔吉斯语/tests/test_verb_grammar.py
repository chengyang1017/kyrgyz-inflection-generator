import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from verb_grammar import (
    converb_p,
    negative_future,
    negative_past_tense,
    present_continuous,
    present_future,
)


def test_oku_examples():
    assert converb_p("оку") == "окуп"
    assert present_continuous("оку", "мен") == "окуп жатамын"
    assert present_continuous("оку", "сен") == "окуп жатасың"
    assert present_continuous("оку", "ал") == "окуп жатат"
    assert present_continuous("оку", "алар") == "окуп жатышат"
    assert negative_past_tense("оку", "мен") == "окубодум"
    assert negative_past_tense("оку", "ал") == "окубоду"
    assert negative_past_tense("оку", "алар") == "окубошту"
    assert negative_future("оку", "ал") == "окубайт"
    assert negative_future("оку", "алар") == "окушпайт"


def test_bil_examples():
    assert negative_past_tense("бил", "мен") == "билбедим"
    assert negative_past_tense("бил", "ал") == "билбеди"
    assert negative_past_tense("бил", "алар") == "билбешти"
    assert negative_future("бил", "ал") == "билбейт"
    assert negative_future("бил", "алар") == "билишпейт"


def test_chyk_examples():
    assert present_future("чык", "мен") == "чыгамын"
    assert present_future("чык", "сен") == "чыгасың"
    assert present_future("чык", "ал") == "чыгат"
    assert present_future("чык", "алар") == "чыгышат"
    assert converb_p("чык") == "чыгып"
    assert negative_future("чык", "ал") == "чыкпайт"
    assert negative_future("чык", "алар") == "чыгышпайт"
