""" The :mod:`adjudicator` contains all classes necessary 
to play a game of Diplomacy, and may be used as a stand
alone module. See the jupyter notebook `examples/game.ipynb`
for a detailed user guide.

"""

from ._build import Build
from ._disband import Disband
from ._force import Force
from ._geography import Geography
from ._location import Location
from ._power import Power
from ._province import Province
from ._season import Season
from ._unit import Unit

from ._map import Map
from ._variant import Variant
from ._retreat import Retreat

__all__ = [
    "Build",
    "Disband",
    "Force",
    "Geography",
    "Location",
    "Map",
    "Power",
    "Province",
    "Retreat",
    "Season",
    "Unit",
    "Variant"
]
