import locale
from urh.util.Logger import logger


class Formatter:
    @staticmethod
    def local_decimal_seperator():
        return locale.localeconv()["decimal_point"]

    @staticmethod
    def science_time(
        time_in_seconds: float, decimals=2, append_seconds=True, remove_spaces=False
    ) -> str:
        if time_in_seconds < 1e-6:
            suffix = "n"
            value = time_in_seconds * 1e9
        elif time_in_seconds < 1e-3:
            suffix = "µ"
            value = time_in_seconds * 1e6
        elif time_in_seconds < 1:
            suffix = "m"
            value = time_in_seconds * 1e3
        else:
            suffix = ""
            value = time_in_seconds

        result = locale.format_string("%.{0}f ".format(decimals) + suffix, value)
        if append_seconds:
            result += "s"
        if remove_spaces:
            result = result.replace(" ", "")

        return result

    @staticmethod
    def big_value_with_suffix(value: float, decimals=3, strip_zeros=True) -> str:
        fmt_str = "%.{0:d}f".format(decimals)
        suffix = ""
        if abs(value) >= 1e9:
            suffix = "G"
            result = locale.format_string(fmt_str, value / 1e9)
        elif abs(value) >= 1e6:
            suffix = "M"
            result = locale.format_string(fmt_str, value / 1e6)
        elif abs(value) >= 1e3:
            suffix = "K"
            result = locale.format_string(fmt_str, value / 1e3)
        else:
            result = locale.format_string(fmt_str, value)

        if strip_zeros:
            result = result.rstrip("0").rstrip(Formatter.local_decimal_seperator())

        return result + suffix

    @staticmethod
    def str2val(str_val, dtype, default=0):
        try:
            return dtype(str_val)
        except (ValueError, TypeError):
            logger.warning(
                "The {0} is not a valid {1}, assuming {2}".format(
                    str_val, str(dtype), str(default)
                )
            )
            return default
