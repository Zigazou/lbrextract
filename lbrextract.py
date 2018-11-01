from struct import unpack
from datetime import datetime, timedelta

def crc16x(buffer: bytes, ignores=[]) -> int:
    crc = 0

    for index, byte in enumerate(buffer):
        if index in ignores:
            byte = 0

        crc ^= byte << 8

        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1

    return crc & 0xffff

def cpm_to_datetime(cpm_date: int, cpm_time: int) -> datetime:
    if cpm_date == 0:
        return None

    hours = (cpm_time >> 11) & 0x1f
    minutes = (cpm_time >> 5) & 0x1f
    seconds = (cpm_time & 0x1f) * 2
    cpm_epoch = datetime(1977, 12, 31, hours, minutes, seconds, tzinfo=None)

    return cpm_epoch + timedelta(days=cpm_date)

class InvalidFilename(Exception):
    pass

class LbrDirectoryEntry:
    ENTRY_FORMAT = "<B8s3sHHHHHHHB5B"
    SECTOR_SIZE = 128

    def __init__(self, data: bytes):
        values = unpack(self.ENTRY_FORMAT, data)
        self.state = values[0]
        self.filename = (
            values[1].decode('ascii').strip(" \x00\t\r\n") + "." +
            values[2].decode('ascii').strip(" \x00\t\r\n")
        ).strip(".")

        self.index = values[3] * self.SECTOR_SIZE
        self.pad_count = values[10] & 0x7f
        self.length = values[4] * self.SECTOR_SIZE - self.pad_count
        self.crc = values[5]

        self.creation = cpm_to_datetime(values[6], values[8])
        self.lastchange = cpm_to_datetime(values[7], values[9])

class MagicNotFound(Exception):
    pass

class InvalidCRC(Exception):
    pass

class LbrDirectory:
    MAGIC = b'\x00           \x00\x00'
    MAGIC_START = 0x00000000
    MAGIC_END = 0x0000000e

    DIRECTORY_START = 0
    CONTROL_ENTRY_START = 0
    CONTROL_ENTRY_END = 32
    ENTRY_SIZE = 32

    CRC_START = 0x10
    CRC_END = 0x12

    def __init__(self, data: bytes):
        self.entries = []
        self.length = 0

        if data[self.MAGIC_START:self.MAGIC_END] != self.MAGIC:
            raise MagicNotFound()

        control_entry = LbrDirectoryEntry(
            data[self.CONTROL_ENTRY_START:self.CONTROL_ENTRY_END]
        )

        self.length = control_entry.length

        crc = unpack("<h", data[self.CRC_START:self.CRC_END])[0]
        crc_calc = crc16x(data[self.DIRECTORY_START:self.length], [0x10, 0x11])

        self.good_crc = crc_calc == crc

        entry_count = control_entry.length // self.ENTRY_SIZE

        for entry_index in range(1, entry_count):
            entry_start = entry_index * self.ENTRY_SIZE
            entry_end = entry_start + self.ENTRY_SIZE
            self.entries.append(LbrDirectoryEntry(data[entry_start:entry_end]))

class LbrArchive:
    def __init__(self, data: bytes):
        self.data = data

        self.directory = LbrDirectory(self.data)
        self.content = self.data[self.directory.length:]

    def getContent(self, entry: LbrDirectoryEntry) -> bytes:
        content = self.data[entry.index:entry.index + entry.length]

        # Check the CRC of the file content.
        if crc16x(content) != entry.crc:
            raise InvalidCRC(entry.filename)

        return content

def main():
    from sys import argv, stderr

    info = stderr

    try:
        lbrarchive = LbrArchive(open(argv[-1], 'rb').read())
    except MagicNotFound:
        print("*** This is not an LBR archive ***", file=stderr)
        return

    if not lbrarchive.directory.good_crc:
        print("*** Invalid CRC for the directory ***", file=stderr)

    print(("S FILENAME      OFFSET  LENGTH  CRC"
           " CREATION            MODIFICATION"), file=info)
    print(("- --------     ------- ------- ----"
           " ------------------- -------------------"), file=info)

    for entry in lbrarchive.directory.entries:
        state = "-"
        crc_ok = "-"
        creation = "no-date"
        lastchange = "no-date"

        try:
            if entry.state == 0:
                state = "+"
                crc_ok = "o"

            if not(entry.creation is None):
                creation = str(entry.creation)

            if not(entry.lastchange is None):
                lastchange = str(entry.lastchange)

            print("{:1} {:12} {:7d} {:7d} {:04X} {:>19} {:>19}".format(
                state, entry.filename, entry.index, entry.length, entry.crc,
                creation, lastchange
            ), file=info)

            # Save the file
            if entry.state == 0:
                with open(entry.filename, "wb") as fileout:
                    fileout.write(lbrarchive.getContent(entry))
        except InvalidCRC as exception:
            print(
                "*** Invalid CRC for {} ***".format(exception.args[0]),
                file=stderr
            )

if __name__ == '__main__':
    main()
