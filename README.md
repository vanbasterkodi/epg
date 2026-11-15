# epg

## UHF guide (`uhf.xmltv.gz`)

`merged.xmltv.gz` is too big for the UHF app (about 245 MB, or 2 GB unzipped). The
**UHF slim EPG** workflow builds `uhf.xmltv.gz` from it twice a day, keeping only the channels
listed in `uhf-channels.txt`, and attaches it to the same `epg` release:

https://github.com/vanbasterkodi/epg/releases/download/epg/uhf.xmltv.gz

Plain XML (no redirect): https://raw.githubusercontent.com/vanbasterkodi/epg/main/uhf.xml

To add a channel to the UHF guide, add its EPG id to `uhf-channels.txt`. The workflow
rebuilds the file as soon as that change is pushed.
