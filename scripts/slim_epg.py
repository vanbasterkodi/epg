#!/usr/bin/env python3
"""Build a small XMLTV guide that the UHF app can download.

merged.xmltv.gz holds ~55,000 channels (about 2 GB unzipped), which is too much for UHF.
This keeps only the channels listed in uhf-channels.txt, streaming the file so memory use
stays small.

Usage: slim_epg.py MERGED.xmltv.gz CHANNELS.txt OUT.xmltv.gz
"""
import gzip
import re
import sys

ATTR_CHANNEL_ID = re.compile(r'\bid="([^"]*)"')
ATTR_PROGRAMME_CHANNEL = re.compile(r'\bchannel="([^"]*)"')


def load_ids(path):
    ids = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                ids.add(line)
    return ids


def main(src, channels_path, dst):
    ids = load_ids(channels_path)
    found = set()
    n_channels = n_programmes = 0

    with gzip.open(src, "rt", encoding="utf-8", errors="replace") as fin, \
            gzip.open(dst, "wt", encoding="utf-8", compresslevel=9) as fout:
        fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fout.write('<!DOCTYPE tv SYSTEM "xmltv.dtd">\n')
        fout.write('<tv generator-info-name="UHF slim EPG (from merged.xmltv.gz)">\n')

        block = None  # lines of the <channel>/<programme> element being read
        keep = False
        closing = None
        for line in fin:
            if block is None:
                s = line.lstrip()
                if s.startswith("<channel "):
                    m = ATTR_CHANNEL_ID.search(s)
                    cid = m.group(1) if m else ""
                    keep, closing = cid in ids, "</channel>"
                    if keep:
                        found.add(cid)
                elif s.startswith("<programme "):
                    m = ATTR_PROGRAMME_CHANNEL.search(s)
                    keep, closing = bool(m) and m.group(1) in ids, "</programme>"
                else:
                    continue
                block = [line] if keep else []
                if closing in line or s.rstrip().endswith("/>"):
                    if keep:
                        fout.write(line)
                        n_channels += closing == "</channel>"
                        n_programmes += closing == "</programme>"
                    block = None
                continue
            if keep:
                block.append(line)
            if closing in line:
                if keep:
                    fout.write("".join(block))
                    n_channels += closing == "</channel>"
                    n_programmes += closing == "</programme>"
                block = None

        fout.write("</tv>\n")

    missing = sorted(ids - found, key=str.lower)
    print(f"Kept {n_channels} channels and {n_programmes} programmes.")
    if missing:
        print(f"{len(missing)} listed ids are not in merged.xmltv.gz: {', '.join(missing)}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
