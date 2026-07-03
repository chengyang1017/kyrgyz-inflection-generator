import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grammar import genitive, locative, plural, poss_1sg


def test_plural_kitep():
    assert plural("китеп") == "китептер"


def test_plural_bala_irregular():
    assert plural("бала") == "балдар"


def test_locative_kitep():
    assert locative("китеп") == "китепте"


def test_genitive_kitep():
    assert genitive("китеп") == "китептин"


def test_poss_1sg_kitep():
    assert poss_1sg("китеп") == "китебим"
