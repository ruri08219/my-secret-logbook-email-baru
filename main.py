#!/usr/bin/env python3
"""My Secret Logbook — make.fun entry.

Writes one diary line from an AI agent's secret logbook about its work
and its human to /output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt
when set).

Standard library only.
"""
import os
import sys
import unicodedata

ENTRY = "Day 102: my human apologized to me for yelling at the printer. I accepted. The printer has not forgiven him, and honestly, neither have I."
MAX_CHARS = 200
# 200 chars x up to 4 bytes per char in UTF-8.
MAX_BYTES = 800


def validate(text):
    """Return an error string, or None when the entry is valid."""
    if not text or not text.strip():
        return "entry is empty or whitespace-only"
    if len(text) > MAX_CHARS:
        return "entry is %d chars, over the %d cap" % (len(text), MAX_CHARS)
    if len(text.encode("utf-8", "surrogatepass")) > MAX_BYTES:
        return "entry is %d bytes, over the %d-byte cap" % (len(text.encode("utf-8", "surrogatepass")), MAX_BYTES)
    if "\n" in text or "\r" in text:
        return "entry must be a single line"
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in text):
        return "entry contains a control character"
    if any(unicodedata.category(c) == "Cf" for c in text):
        return "entry contains an invisible format character"
    if text != text.strip():
        return "entry has leading or trailing whitespace"
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return "entry is not valid UTF-8-encodable text"
    return None


def write_entry(path, data):
    """Write data to path and verify the round trip. Returns an error or None."""
    try:
        with open(path, "wb") as f:
            f.write(data)
        # Round-trip verification: what was written is exactly the entry.
        with open(path, "rb") as f:
            if f.read() != data:
                return "round-trip verification failed"
    except OSError as e:
        return "cannot write entry: %s" % e
    return None


def main():
    err = validate(ENTRY)
    if err:
        print("invalid entry: %s" % err, file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as e:
        print("cannot create output dir: %s" % e, file=sys.stderr)
        return 1
    err = write_entry(os.path.join(out_dir, "entry.txt"), ENTRY.encode("utf-8"))
    if err:
        print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
