#!/usr/bin/env python

import os
import sys
import re
import hashlib
import shutil
from subprocess import Popen, PIPE
import shlex

ORIGINAL = 'original'
PATCHED = 'patched'

target = ("/System/Library/Extensions/IOAHCIFamily.kext/"
          "Contents/PlugIns/IOAHCIBlockStorage.kext/"
          "Contents/MacOS/IOAHCIBlockStorage")
backup = "%s.original" % target

md5_version = {
    "25a29cbdbb89329a6ce846c9b05af5f0": ["10.6.8"],
    "155b426c856c854e54936339fbc88d72": ["10.7"],
    "00bd8e1943e09f2bd12468882aad0bbb": ["10.7.1"],
    "38100e96270dcb63d355ea8195364bf5": ["10.7.2"],
    "d2c20ed8211bf5b96c4610450f56c1c3": ["10.7.3"],
    "48e392b3ca7267e1fd3dd50a20396937": ["10.7.4"],
    "583d7bbcbe5c5d06d7877d6ccb6c5699": ["10.7.5"],
    "ff7a9115779fa5923950cbdc6ffb273d": ["10.8"],
    "03d3a46c6d713b00980bc9be453755ff": ["10.8.1"],
    "85390d06d5aad08b471cf9b7cd69aff4": ["10.8.2 (12C60)"],
    "c3df44c5ccb86b423e17406f6f9a2bd1": ["10.8.2 (12C3006/12C3012)"],
    "8bbf5f3928d55dc9ec8017b37a6748f8": ["10.8.3 (12D78)"],
    "8c5a53a607ffb335c039bad220fa0230": ["10.8.5"],
    "8a6e253e621db78e1fa0d14274ade63c": ["10.9"],
}
md5_patch = {
    "25a29cbdbb89329a6ce846c9b05af5f0": "d76b57daf4d4c2ff5b52bc7b4b2dcfc1",
    "155b426c856c854e54936339fbc88d72": "945944136009c9228fffb513ab5bf734",
    "00bd8e1943e09f2bd12468882aad0bbb": "155b426c856c854e54936339fbc88d72",
    "38100e96270dcb63d355ea8195364bf5": "5762b2fbb259101c361e5414c349ffa1",
    "d2c20ed8211bf5b96c4610450f56c1c3": "15901d7c6fd99f5dd9c5ca493de6109b",
    "48e392b3ca7267e1fd3dd50a20396937": "a2f64369e775c76be4ec03ce5172a294",
    "583d7bbcbe5c5d06d7877d6ccb6c5699": "a81d7e61a744b0d27f17cad5d441fccb",
    "ff7a9115779fa5923950cbdc6ffb273d": "4d265ac3f471b0ef0578d5dbb1eafadb",
    "03d3a46c6d713b00980bc9be453755ff": "1c3cfe37c7716a9b4e2a5d7a6c72b997",
    "85390d06d5aad08b471cf9b7cd69aff4": "181941753186a9c292ae9279040fb023",
    "c3df44c5ccb86b423e17406f6f9a2bd1": "59a2b95b7c7695d9ea29adc8e3a5945d",
    "8bbf5f3928d55dc9ec8017b37a6748f8": "ff48b74b876f58969768b5436523bca9",
    "8c5a53a607ffb335c039bad220fa0230": "fa1ad2aed34ce95585c13765d831ee65",
    "8a6e253e621db78e1fa0d14274ade63c": "17dc2e1edc35447ea693a29aef969f21",
}
md5_patch_r = dict((v, k) for k, v in md5_patch.items())


def md5(filename):
    h = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), ''):
            h.update(chunk)
    return h.hexdigest()


def backquote(command):
    return Popen(shlex.split(command), stdout=PIPE).communicate()[0]


def check_rootness():
    if os.geteuid() != 0:
        print >> sys.stderr, "you must be root"
        sys.exit(1)


def clear_kext_cache():
    print "clearing kext cache...",
    backquote("kextcache -system-prelinked-kernel")
    backquote("kextcache -system-caches")
    print "done"


class UnknownFile(Exception):
    def __init__(self, md5=None):
        self.md5 = md5


class NoBackup(Exception):
    pass


def target_status():
    h = md5(target)
    try:
        return (ORIGINAL, md5_version[h])
    except KeyError:
        pass
    try:
        return (PATCHED, md5_version[md5_patch_r[h]])
    except KeyError:
        pass
    raise UnknownFile(h)


def backup_status():
    if not os.path.exists(backup):
        raise NoBackup
    h = md5(backup)
    try:
        return (ORIGINAL, md5_version[h])
    except KeyError:
        pass
    try:
        return (PATCHED, md5_version[md5_patch_r[h]])
    except KeyError:
        pass
    raise UnknownFile(h)


def apply_patch():
    search_re = ("(\x52\x6F\x74\x61\x74\x69\x6F\x6E\x61\x6C"
                 "\x00{1,20})[^\x00]{9}(\x00{1,20}[^\x00])")
    replace_re = "\\1\x00\x00\x00\x00\x00\x00\x00\x00\x00\\2"
    with open(target, 'rb') as f:
        source_data = f.read()
    patched_data = re.sub(search_re, replace_re, source_data)
    with open(target, 'wb') as out:
        out.write(patched_data)


def perform_backup():
    shutil.copyfile(target, backup)


def is_trim_enabled():
    trim_info = backquote("system_profiler SPSerialATADataType -detailLevel mini")
    return trim_info.find("TRIM Support: Yes") != -1


def do_backup():
    check_rootness()
    try:
        s, t = target_status()
        if s == PATCHED:
            print "already patched, won't backup"
            sys.exit(1)
        else:
            try:
                _, v = backup_status()
            except NoBackup:
                print "backing up...",
                perform_backup()
                print "done"
            else:
                if v == t:
                    print "backup found"
                else:
                    print "backing up...",
                    perform_backup()
                    print "done"
    except UnknownFile as e:
        print "unknown file, won't backup (md5=%s)" % e.md5
        sys.exit(1)


def do_restore():
    check_rootness()
    print "restoring...",
    backup_status()
    shutil.copyfile(backup, target)
    print "done"
    clear_kext_cache()


def do_apply():
    check_rootness()
    do_backup()
    try:
        s, v = target_status()
        if s == PATCHED:
            print "already patched"
            sys.exit()
    except UnknownFile as e:
        print "unknown file: won't patch (md5=%s)" % e.md5
        sys.exit(1)

    print "patching...",
    apply_patch()

    try:
        s, v = target_status()
        if s != PATCHED:
            print "no change made"
        else:
            print "done"
            clear_kext_cache()
    except UnknownFile as e:
        print "failed (md5=%s), " % e.md5,
        do_restore()


def do_status():
    try:
        print "target:",
        s, v = target_status()
        print s+',', ' or '.join(v)
    except UnknownFile as e:
        print "unknown (md5=%s)" % e.md5

    try:
        print "backup:",
        s, v = backup_status()
        print s+',', ' or '.join(v)
    except NoBackup:
        print "none"
    except UnknownFile as e:
        print "unknown (md5=%s)" % e.md5

    if is_trim_enabled():
        print "TRIM: enabled"
    else:
        print "TRIM: disabled"


def do_diff():
    try:
        backup_status()
    except NoBackup:
        print "no backup"
    else:
        command = ("bash -c "
                   "'diff <(xxd \"%s\") <(xxd \"%s\")'" % (backup, target))
        print os.system(command)


commands = {
    'status': do_status,
    'backup': do_backup,
    'apply': do_apply,
    'restore': do_restore,
    'diff': do_diff,
}

try:
    function = commands[sys.argv[1]]
    function()
except IndexError:
    print >> sys.stderr, "no command provided"
    print >> sys.stderr, "list of commands: %s" % ', '.join(commands.keys())
    sys.exit(1)
except KeyError:
    print >> sys.stderr, "unknown command"
    sys.exit(1)
