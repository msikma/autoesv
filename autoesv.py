#!/usr/bin/env python
# coding=utf8
# (C) Michiel Sikma, MIT License

'''
Copies Pokémon egg files (.pk6, .pk7) to a subdirectory based on their ESVs.
Note: ESV = Egg Shiny Value and is an integer from 0-4095.
'''
from struct import calcsize, unpack
from collections import namedtuple
from sys import exit
from os import listdir, getcwd, makedirs, access, W_OK
from shutil import copy2
from os.path import basename, join, splitext, abspath, exists
import argparse

class tcolors:
  '''Color escape codes for output.'''
  YELLOW = '\033[93m'
  GREEN = '\033[92m'
  CYAN = '\033[36m'
  RED = '\033[31m'
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
  print('{}[{}] {}Species: {}{:03d} {}TID:  {}{:05d} {}SID: {}{:05d} {}PID: {}0x{:08X} {}TSV: {}{:04d} {}ESV: {}{:04d}'.format(
    tcolors.YELLOW,
    basename(file),
    tcolors.GREEN, tcolors.CYAN, pkinfo.species,
    tcolors.GREEN, tcolors.CYAN, pkinfo.tid,
    tcolors.GREEN, tcolors.CYAN, pkinfo.sid,
    tcolors.GREEN, tcolors.CYAN, pkinfo.pid,
    tcolors.GREEN, tcolors.CYAN, get_tsv(pkinfo.tid, pkinfo.sid),
    tcolors.GREEN, tcolors.YELLOW, get_esv(pkinfo.pid),
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
    tcolors.GREEN, tcolors.YELLOW, get_esv(pkinfo.pid),
    tcolors.RESET
  ))

def process_pkx(file, out_dir, pk_dir):
  '''
  Processes a single .pk6/.pk7 file. Prints some basic info about the file
  and then moves it to the target directory based on its ESV.
  '''
  data = read_bin(file)
  ftype = splitext(file)[1][1:]  # Either 'pk6' or 'pk7'

  if ftype == 'pk6':
    pkinfo = extract_pkdata(data)
    esv = get_esv(pkinfo.pid)
    dir_name = ensure_dir(out_dir, esv, 'PK6' if pk_dir else '')
    copy_file(dir_name, file)
    print_pk6info(file, pkinfo)

  if ftype == 'pk7':
    pkinfo = extract_pkdata(data)
    esv = get_esv(pkinfo.pid)
    dir_name = ensure_dir(out_dir, esv, 'PK7' if pk_dir else '')
    copy_file(dir_name, file)
    print_pk7info(file, pkinfo)

def ensure_dir(out_dir, esv='', pkx=''):
  # Be careful, ESV can be 0. Can't just do 'if esv'!
  has_esv = esv != ''

  dir_name = '{}{}{}{}{}'.format(
    out_dir,
    '/' if has_esv and pkx else '',
    pkx,
    '/' if has_esv else '',
    '{:04}'.format(esv) if has_esv else ''
  )
  try:
    if not exists(dir_name):
      makedirs(dir_name)
  except:
    pass
  if not access(dir_name, W_OK):
    raise IOError('No write access to directory: {}'.format(dir_name))

  return dir_name

def copy_file(dest_dir, file):
  new_name = '{}/{}'.format(dest_dir, basename(file))
  copy2(file, new_name)

def process_in_dir(in_dir, out_dir, pk_dir):
  for file in listdir(in_dir):
    current = join(in_dir, file)
    process_pkx(current, out_dir, pk_dir)

def main():
  parser = argparse.ArgumentParser(description='Organizes Pokémon egg files (.pk6 and .pk7) based on their ESV. The egg files are read from a source directory and then copied to a destination directory, separated in subdirectories named after the egg\'s ESV. If --pk-dir is enabled, the resulting file structure is: {PK6,PK7} > {$ESV} > ... .pk6 or .pk7 files.')

  parser.add_argument('src', type=str, help='source directory containing unsorted egg files')
  parser.add_argument('dst', type=str, help='destination directory to copy results to')
  parser.add_argument('--pk-dir', action='store_true', help='copies files to a top "pk6" and "pk7" directory')
  args = parser.parse_args()

  in_dir = abspath('{}/{}'.format(getcwd(), args.src))
  out_dir = abspath('{}/{}'.format(getcwd(), args.dst))
  print('Processing files in directory: {}'.format(in_dir))
  print('Saving to directory: {}'.format(out_dir))

  # Ensure that our output directory exist.
  # ESV and PK6/PK7 directories are made as needed during processing.
  try:
    ensure_dir(out_dir)
  except IOError as err:
    print('{}{}{}'.format(tcolors.RED, str(err), tcolors.RESET))
    exit(1)

  process_in_dir(in_dir, out_dir, args.pk_dir)

main()
