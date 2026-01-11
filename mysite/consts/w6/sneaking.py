from consts.consts_autoreview import ValueToMulti
from consts.idleon.lava_func import lava_func

pristine_charm_images_override = {
    # we have to deduplicate from the `Cotton Candy` meal
    "Cotton Candy": "cotton-candy-charm"
}


def getMoissaniteValue(moissaniteLevel: int):
    value = 0
    try:
        if moissaniteLevel > 0:
            value = sneaking_gemstones_dict["Moissanite"]["Base Value"] + (
                sneaking_gemstones_dict["Moissanite"]["Scaling Value"]
                * (moissaniteLevel / (moissaniteLevel + 1000))
            )
        return value
    except:
        return value


def getGemstoneBoostedValue(
    gemstone_value: float, moissanite_value: float, talent_level: int
):
    if moissanite_value > 0:
        moissanite_multi = ValueToMulti(moissanite_value)
        talent_level_multi = lava_func("decayMulti", max(0, talent_level), 3, 300)
        boostedValue = gemstone_value * moissanite_multi * talent_level_multi
        return boostedValue
    else:
        return gemstone_value


def getGemstoneBaseValue(gemstoneName: str, gemstoneLevel: int):
    value = 0
    if gemstoneLevel > 0:
        if gemstoneName in sneaking_gemstones_dict:
            value = sneaking_gemstones_dict[gemstoneName]["Base Value"] + (
                sneaking_gemstones_dict[gemstoneName]["Scaling Value"]
                * (gemstoneLevel / (gemstoneLevel + 1000))
            )
        else:
            logger.warning(
                f"Unrecognized gemstoneName: '{gemstoneName}'. Returning default 0 value"
            )
    return value


def getGemstonePercent(gemstone_name: str, gemstone_value: float):
    try:
        return 100 * (
            gemstone_value / sneaking_gemstones_dict[gemstone_name]["Max Value"]
        )
    except Exception as reason:
        logger.exception(
            f"Could not find max value for Gemstone {gemstone_name} given value {gemstone_value} because: {reason}"
        )
    pass
