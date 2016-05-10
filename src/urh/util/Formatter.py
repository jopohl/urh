import locale


# locale.setlocale(locale.LC_ALL, '')
from urh.util.Logger import logger


class Formatter():
    @staticmethod
    def science_time(time_in_seconds: float) -> str:
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

        return locale.format_string("%.2f " + suffix, value) + "s"

    @staticmethod
    def big_value_with_suffix(value: float, decimals=3) -> str:
        fmt_str = "%.{0:d}f".format(decimals)
        if abs(value) >= 1e9:
            return locale.format_string(fmt_str+"G", value / 1e9)
        elif abs(value) >= 1e6:
            return locale.format_string(fmt_str+"M", value / 1e6)
        elif abs(value) >= 1e3:
            return locale.format_string(fmt_str+"K", value / 1e3)
        else:
            return locale.format_string(fmt_str, value)


    @staticmethod
    def str2val(str_val, dtype, default=0):
        try:
            return dtype(str_val)
        except (ValueError, TypeError):
            logger.warning("The {0} is not a valid {1}, assuming {2}".format(str_val, str(dtype), str(default)))
            return default