#!/usr/bin/python

from __future__ import print_function

import sys
import argparse
import array


def parse_args(argv):
    parser = argparse.ArgumentParser(prog=argv[0])
    parser.add_argument("source", help="File containing HID descriptor (- for stdin)")
    parser.add_argument("destination", help="Destination C header file (- for stdout)", default="-", nargs="?")
    parser.add_argument("-format", choices=("raw", "hex"), default="hex", help="Input file format")
    parser.add_argument("-name", default="REPORT_DESCRIPTOR", help="resulting uint8_t array name")
    parser.add_argument("-maxline", type=int, default=8, help="Highest number of hex pairs permissible per line")
    return parser.parse_args(argv[1:])

def read_raw(file):
    a = array.array("B")
    a.fromstring(file.read())
    return a

def read_hex(file):
    content = file.read().replace(" ", "")
    a = [int(content[i:i+2], 16) for i in range(0, len(content)-1, 2)]
    return a

def main(argv):
    args = parse_args(argv)

    if args.source == "-":
        infile = sys.stdin
    else:
        infile = open(args.source, "rb")

    if args.format == "hex":
        data = read_hex(infile)
    else:
        data = read_raw(infile)

    if args.source != "=":
        infile.close()

    fdata = ["0x%02x" % i for i in data]

    if args.destination == "-":
        outfile = sys.stdout
    else:
        outfile = open(args.destination, "wb")

    outfile.write("// Generated by muhid convert_descriptor.py\n")
    outfile.write("\n")
    outfile.write("#include <stdint.h>\n")
    outfile.write("\n")
    outfile.write("size_t const %s_SIZE = %i;\n" % (args.name, len(fdata)))
    outfile.write("uint8_t const %s[] = {\n" % args.name)
    for i in range(0, len(fdata), args.maxline):
        outfile.write("\t%s,\n" % ", ".join(fdata[i:min(len(fdata), i+args.maxline)]))
    outfile.write("};\n")

    if args.destination != "-":
        outfile.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

