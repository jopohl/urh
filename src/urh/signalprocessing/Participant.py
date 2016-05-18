class Participant(object):
    def __init__(self, name: str, shortname: str = None, address_hex: str = None):
        self.name = name if name else "unknown"
        self.shortname = name[0].upper() if shortname else shortname
        self.address_hex = address_hex if address_hex else ""