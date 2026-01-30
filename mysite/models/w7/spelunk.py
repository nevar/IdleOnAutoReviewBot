from consts.consts_autoreview import EmojiType, ValueToMulti
from consts.idleon.lava_func import lava_func
from consts.idleon.w7.spelunk import spelunking_cave_list, spelunk_chapters
from consts.w7.spelunk import chapter_name, chapter_bonus_img

from models.advice.advice import Advice

from utils.number_formatting import round_and_trim
from utils.safer_data_handling import safe_loads, safer_index
from utils.logging import get_logger

logger = get_logger(__name__)


class SpelunkCave:
    def __init__(self, index: int, info: dict, state: int):
        self.name = info["Name"]
        self._description = info["Description"]
        self.bonus_obtained = bool(state)
        self._image = f"spelunking-boss-{index}"
        self._resource = f"spelunking-cavern-{index}"

    def get_bonus_advice(self, link_to_section: bool = True) -> Advice:
        label = ""
        if link_to_section:
            label += "{{ Spelunking|#spelunking }} - "
        label += f"{self.name}:<br>{self._description}"
        return Advice(
            label=label,
            picture_class=self._image,
            progression=int(self.bonus_obtained),
            goal=1,
            resource=self._resource,
        )

    def get_unlock_advice(self) -> Advice:
        return Advice(
            label="{{Spelunking|#spelunking}}:<br>"
            f"Defeat the Boss of the {self.name} Cave",
            picture_class=self._image,
            progression=int(self.bonus_obtained),
            goal=1,
        )


class LoreBonus:
    def __init__(self, chapter_index: int, index: int, info: dict, level: int):
        self.level = level
        self._template = info["Description"]
        self._image = chapter_bonus_img[index]
        self._x1 = info["x1"]
        self._x2 = info["x2"]
        self._lava_fun = info["LavaFun"]
        self._min_page = info["MinPage"]
        self._multi_by_artifact = info["MultiByArtifact"]
        self.value = 0
        self.max_value = None
        self._resource = f"spelunking-chapter-{chapter_index + 1}"

    def calculate_bonus(self, multi):
        multi = self._multi_by_artifact * multi
        self.value = multi * lava_func(self._lava_fun, self.level, self._x1, self._x2)
        match self._lava_fun:
            case "decay":
                self.max_value = self._x1 * multi
            case "decayMulti":
                self.max_value = (1 + self._x1) * multi
            case _:
                self.max_value = None

    def get_bonus_advice(self, link_to_section: bool = True) -> Advice:
        label = ""
        if link_to_section:
            label += "{{ Lore Chapters Bonus|#spelunking }}:<br>"
        value = f"{round_and_trim(self.value)}"
        if self.max_value is not None:
            value += f"/{round_and_trim(self.max_value)}"
        bonus = self._template.replace("{", value).replace("}", value)
        if not link_to_section:
            label += f"Level {self.level}: {bonus}"
            label += f"<br>Required pages: {self._min_page}"
            if self.max_value is not None:
                progress = f"{self.value / self.max_value:.2%}"
                goal = "100%"
            else:
                progress = "Linear"
                goal = EmojiType.INFINITY.value
        else:
            label += bonus
            progress = self.level
            goal = EmojiType.INFINITY.value
        return Advice(
            label=label,
            picture_class=self._image,
            resource=self._resource,
            progression=progress,
            goal=goal,
        )


class Spelunk:
    def __init__(self, raw_data: dict):
        spelunk_info = safe_loads(raw_data.get("Spelunk", []))
        raw_cave_state: list[int] = safer_index(spelunk_info, 0, [])
        if not raw_cave_state:
            logger.warning("Spelunk Cave data not present.")
        self.cave: dict[str, SpelunkCave] = {}
        for index, cave_info in enumerate(spelunking_cave_list):
            cave_state = safer_index(raw_cave_state, index, 0)
            cave = SpelunkCave(index, cave_info, cave_state)
            self.cave[cave.name] = cave
        raw_chapter_bonus_level: list[int] = safer_index(spelunk_info, 8, [])
        self.lore: dict[str, list[LoreBonus]] = {name: [] for name in chapter_name}
        for index, chapter in enumerate(spelunk_chapters):
            name = chapter_name[index]
            for bonus_index, info in enumerate(chapter):
                level_index = index * 4 + bonus_index
                bonus_level = safer_index(raw_chapter_bonus_level, level_index, 0)
                lore_bonus = LoreBonus(index, level_index, info, bonus_level)
                self.lore[name].append(lore_bonus)

    def calculate_lore_bonus(self, artifact):
        self.lore_multi = ValueToMulti(30 * artifact["Level"])
        for chapter_bonuses in self.lore.values():
            for bonus in chapter_bonuses:
                bonus.calculate_bonus(self.lore_multi)
