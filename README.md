lbrextract
==========

`lbrextract.py` is a Python 3 command line script that extract files contained
in an LBR archive.

LBR archives are used under the CP/M operating system. They contain files with
no compression at all but with CRC checks.

[More information about LBR archives and its file format](https://www.seasip.info/Cpm/ludef5.html).

Usage
-----

The script takes one parameter, the archive file name, and extracts its content
in the current directory.

Ex:

    $ python3 lbrextract.py 3pmtp2.lbr

    *** Invalid CRC for the directory ***
    S FILENAME      OFFSET  LENGTH  CRC CREATION            MODIFICATION
    - --------     ------- ------- ---- ------------------- -------------------
    + SPPMAIN.CMD      896     128 B926             no-date             no-date
    + SB001.CMD       1024     128 337A             no-date             no-date
    + SB006.CMD       1152     128 5213             no-date             no-date
    + SB007.CMD       1280     128 8919             no-date             no-date
    + E2.CMD          1408     128 F2A7             no-date             no-date
    + E3.CMD          1536     128 AE3D             no-date             no-date
    + SB003.CMD       1664     128 6B0B             no-date             no-date
    + SB004.CMD       1792     128 8D40             no-date             no-date
    + SB008.CMD       1920     128 92D6             no-date             no-date
    + SB00A.CMD       2048     128 4188             no-date             no-date
    + LINKSPP.SUB     2176     256 3453             no-date             no-date
    + SBIFDEF.LIB     2432     896 816F             no-date             no-date
    + SMALLERR.TXT    3328    1152 E173             no-date             no-date
    + SPP.004         4480   12672 F614             no-date             no-date
    + SPP.002        17152   27648 14D6             no-date             no-date
    + SPP.COM        44800    5376 AF80             no-date             no-date
    + SPP.001        50176    6272 0856             no-date             no-date
    + SPP.007        56448    1792 EB6B             no-date             no-date
    + SPP.006        58240    5376 9215             no-date             no-date
    + SPP.008        63616   13056 02C1             no-date             no-date
    + SPP.009        76672    6528 02CD             no-date             no-date
    + SPP.003        83200   14464 EF00             no-date             no-date
    + SPP.00A        97664   13056 4CF6             no-date             no-date
    -                    0       0 0000             no-date             no-date
    -                    0       0 0000             no-date             no-date
    -                    0       0 0000             no-date             no-date
    -                    0       0 0000             no-date             no-date

Notes
-----

The first column indicates the entry state. A `+` indicates a valid entry. A `-`
indicates a deleted or unused entry.

Creation date and modification date are optional.

File length is usually a multiple of 128. The extraction understands precise
file length when the archive uses it.

If the directory CRC is wrong, the extraction still occurs.

If the file CRC is wrong, the extraction of the file does not occur.