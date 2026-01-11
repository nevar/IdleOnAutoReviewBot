from math import floor

from consts.consts_autoreview import ValueToMulti, MultiToValue, EmojiType

# TODO: move to idleon.w6.sneaking
from consts.idleon.w6.sneaking import pristine_charms_info
from consts.w6.sneaking import (
    pristine_charm_images_override,
    # sneaking_gemstones_dict,
    # getGemstoneBaseValue,
    # getGemstonePercent,
    # jade_emporium,
    # jade_emporium_order,
)


from models.advice.advice import Advice

from utils.number_formatting import round_and_trim
from utils.safer_data_handling import safe_loads, safer_index
from utils.text_formatting import notateNumber, kebab

from utils.logging import get_logger

logger = get_logger(__name__)


class Pristine:
    def __init__(self, name: str, is_obtained: bool):
        self.name = name
        self.obtained = is_obtained
        info = pristine_charms_info[name]
        description_template = info["Description"]
        self.value = info["Value"] if is_obtained else 0
        if "}" in description_template:
            self._description = description_template.replace(
                "}", f"{ValueToMulti(self.value)}"
            )
        else:
            self._description = description_template.replace("{", f"{self.value}")
        name_for_image = pristine_charm_images_override.get(name, name)
        self._image = kebab(name_for_image)

    def get_obtained_advice(self, link_to_section: bool = True):
        label = ""
        if link_to_section:
            label += "{{Pristine Charms|#sneaking}} - "
        label += f"{self.name}:"
        label += f"<br>{self._description}"
        return Advice(
            label=label,
            picture_class=self._image,
            progression=int(self.obtained),
            goal=1,
        )


class Sneaking:
    def __init__(self, raw_data):
        raw_optlacc = raw_data.get("OptLacc", [])
        self.current_mastery = safer_index(raw_optlacc, 231, 0)
        self.unlocked_mastery = safer_index(raw_optlacc, 232, 0)
        self.pristine: dict[str, Pristine] = {}
        # self.gemstone: dict[str, Gemstone] = []
        # self.emporium: set[str] = set()
        raw_ninja_list = safe_loads(raw_data.get("Ninja", []))
        if not raw_ninja_list:
            logger.warning("Sneaking data not present.")
        self._parse_pristine(raw_ninja_list)
        # _parse_w6_gemstones(account)
        # _parse_w6_jade_emporium(account, raw_ninja_list)

    def _parse_pristine(self, raw_ninja_list):
        if raw_ninja_list:
            raw_pristine_charms_list = raw_ninja_list[107]
        else:
            raw_pristine_charms_list = [0] * len(pristine_charms_info)
        for index, name in enumerate(pristine_charms_info.keys()):
            is_obtained = bool(raw_pristine_charms_list[index])
            self.pristine[name] = Pristine(name, is_obtained)
