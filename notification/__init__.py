VERSION = (0, 1, 4, "final")


def get_version():
    if VERSION[3] != "final":
        return f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}{VERSION[3]}"
    else:
        return f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}"


__version__ = get_version()
