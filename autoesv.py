#!/usr/bin/env python
# coding=utf8
# (C) Michiel Sikma, MIT License

'''
Copies Pokémon egg files (.pk6, .pk7) to a subdirectory based on their ESVs.
Note: ESV = Egg Shiny Value and is an integer from 0-4095.
'''
from struct import calcsize, unpack
from collections import namedtuple
from os import listdir, getcwd, makedirs
from shutil import copy2
from os.path import basename, join, splitext, abspath, exists
import argparse

class tcolors:
  '''Color escape codes for output.'''
  YELLOW = '\033[93m'
  GREEN = '\033[92m'
  CYAN = '\033[36m'
  RESET = '\033[00m'

def get_tsv(tid, sid):
  '''Returns the TSV of a trainer's ID and secret ID.'''
  return (tid ^ sid) >> 4

def get_esv(pid):
  '''Returns the ESV of an egg.'''
  if (pid > 0xffffffff):
    raise ValueError('PID is invalid: {}'.format(hex(pid)))
  high = pid >> 16
  low = pid & 0xffff
  return (low ^ high) >> 4

def read_bin(file):
  '''Reads a file into a buffer as binary data all at once.'''
  with open(file, 'rb') as f:
    return f.read()

def extract_pkdata(data):
  # Returns a named tuple with information about this pk6 file.
  #
  # Note that this extracts "training_bag_hits" and "training_bag",
  # which do not exist in pk7 files. We ignore this because we're
  # not using them anyway.
  #
  # This information was taken from PKHeX:
  # <https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/PKM/PK6.cs>
  Pokemon = namedtuple('Pokemon', 'encryption_constant sanity checksum species held_item tid sid exp ability ability_number training_bag_hits training_bag pid')
  frm = '<IHHHHHHIBBBBI'
  return Pokemon._make(unpack(frm, data[:calcsize(frm)]))

def print_pk6info(file, pkinfo):
  '''Prints some basic information about a Pokémon pk6 file.'''
  print('{}[{}] {}Species: {}{:03d} {}TID: {}{:06d} {}SID: {}{:05d} {}PID: {}0x{:08X} {}TSV: {}{:04d} {}ESV: {}{:04d}'.format(
    tcolors.YELLOW,
    basename(file),
    tcolors.GREEN, tcolors.CYAN, pkinfo.species,
    tcolors.GREEN, tcolors.CYAN, pkinfo.tid,
    tcolors.GREEN, tcolors.CYAN, pkinfo.sid,
    tcolors.GREEN, tcolors.CYAN, pkinfo.pid,
    tcolors.GREEN, tcolors.CYAN, get_tsv(pkinfo.tid, pkinfo.sid),
    tcolors.GREEN, tcolors.CYAN, get_esv(pkinfo.pid),
    tcolors.RESET
  ))


def print_pk7info(file, pkinfo):
  '''Prints some basic information about a Pokémon pk7 file.'''
  # In generation 7, there's a raw value for the TID and SID but they are
  # displayed a little different in-game.
  # TID = TID + SID * 0x10000 (which is 65536)
  sid_str = '{:010d}'.format(pkinfo.sid * 0x10000)[:4]
  sid = int(sid_str)
  tid = pkinfo.tid + pkinfo.sid * 0x10000
  tid_str = str(tid)[-6:]

  print('{}[{}] {}Species: {}{:03d} {}TID: {}{} {}SID:  {}{:04d} {}PID: {}0x{:08X} {}TSV: {}{:04d} {}ESV: {}{:04d}'.format(
    tcolors.YELLOW,
    basename(file),
    tcolors.GREEN, tcolors.CYAN, pkinfo.species,
    tcolors.GREEN, tcolors.CYAN, tid_str,
    tcolors.GREEN, tcolors.CYAN, sid,
    tcolors.GREEN, tcolors.CYAN, pkinfo.pid,
    tcolors.GREEN, tcolors.CYAN, get_tsv(pkinfo.tid, pkinfo.sid),
    tcolors.GREEN, tcolors.CYAN, get_esv(pkinfo.pid),
    tcolors.RESET
  ))

def process_pkx(file, out_dir):
  '''
  Processes a single .pk6/.pk7 file. Prints some basic info about the file
  and then moves it to the target directory based on its ESV.
  '''
  data = read_bin(file)
  ftype = splitext(file)[1][1:]  # Either 'pk6' or 'pk7'

  if ftype == 'pk6':
    pkinfo = extract_pkdata(data)
    print_pk6info(file, pkinfo)
    esv = get_esv(pkinfo.pid)
    ensure_dir(esv, out_dir)
    copy_file(esv, out_dir, file)

  if ftype == 'pk7':
    pkinfo = extract_pkdata(data)
    print_pk7info(file, pkinfo)
    esv = get_esv(pkinfo.pid)
    ensure_dir(esv, out_dir)
    copy_file(esv, out_dir, file)

def ensure_dir(esv, out_dir):
  dir_name = '{}/{:04}'.format(out_dir, esv)
  if not exists(dir_name):
    makedirs(dir_name)

def copy_file(esv, out_dir, file):
  new_name = '{}/{:04}/{}'.format(out_dir, esv, basename(file))
  copy2(file, new_name)

def process_in_dir(in_dir, out_dir):
  for file in listdir(in_dir):
    current = join(in_dir, file)
    process_pkx(current, out_dir)

def main():
  parser = argparse.ArgumentParser(description='Organizes Pokémon egg files (.pk6 and .pk7) based on their ESV. The egg files are read from a source directory and then copied to a destination directory, separated in subdirectories named after the egg\'s ESV.')

  parser.add_argument('src', type=str, help='source directory containing unsorted egg files')
  parser.add_argument('dst', type=str, help='destination directory to copy results to')
  args = parser.parse_args()

  in_dir = abspath('{}/{}'.format(getcwd(), args.src))
  out_dir = abspath('{}/{}'.format(getcwd(), args.dst))
  print('Processing files in directory: {}'.format(in_dir))
  print('Saving to directory: {}'.format(out_dir))
  process_in_dir(in_dir, out_dir)

main()
