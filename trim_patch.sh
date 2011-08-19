#!/bin/bash

target="/System/Library/Extensions/IOAHCIFamily.kext/Contents/PlugIns/IOAHCIBlockStorage.kext/Contents/MacOS/IOAHCIBlockStorage"
backup="$target.original"

original_md5="155b426c856c854e54936339fbc88d72"
modified_md5="945944136009c9228fffb513ab5bf734"

error() {
    echo "$1"
    exit $2
}

md5() {
  /sbin/md5 "$1" | sed 's/.*= //'
}

check_original() {
    case $(md5 "$1") in
        $original_md5)
            return 0
            ;;
        $modified_md5)
            return 1
            ;;
        *)
            return 255
            ;;
    esac
}

check_modified() {
    case $(md5 "$1") in
        $modified_md5)
            return 0
            ;;
        $original_md5)
            return 1
            ;;
        *)
            return 255
            ;;
    esac
}

check_status() {
    case $(md5 "$1") in
        $modified_md5)
            return 1
            ;;
        $original_md5)
            return 0
            ;;
        *)
            return 255
            ;;
    esac
}

backup() {
    if [ ! -f "$backup" ]; then
        sudo cp "$target" "$backup"
    fi
}

restore() {
    if [ -f "$backup" ]; then
        sudo cp "$backup" "$target"
    else
        echo "no backup found"
        return 1
    fi
}

apply_patch() {
    sudo perl -pi -e 's|(\x52\x6F\x74\x61\x74\x69\x6F\x6E\x61\x6C\x00).{9}(\x00\x51)|$1\x00\x00\x00\x00\x00\x00\x00\x00\x00$2|sg' "$1"
}

revert_patch() {
    sudo perl -pi -e 's|(\x52\x6F\x74\x61\x74\x69\x6F\x6E\x61\x6C\x00).{9}(\x00\x51)|$1\x41\x50\x50\x4C\x45\x20\x53\x53\x44$2|sg' "$1"
}

clear_cache() {
    sudo kextcache -system-prelinked-kernel
    sudo kextcache -system-caches
}

case "$1" in
    --apply)
        check_original "$target" || error "unknown file" 1
        backup || error "backup failed" 2
        apply_patch "$target" || error "patch failed" 3
        check_modified "$target" || error "patch failed" 4
        clear_cache
        ;;
    --revert)
        check_modified "$target" || error "unknown file" 1
        revert_patch "$target" || error "revert failed" 3
        check_original "$target" || error "revert failed" 1
        clear_cache
        ;;
    --restore)
        restore || error "restore failed" 2
        clear_cache
        ;;
    --status)
        check_status "$target"
        case $? in
            0)
                echo "original: $target"
                ;;
            1)
                echo "patched: $target"
                ;;
            *)
                echo "unknown: $target"
                ;;
        esac
        test -f "$backup" && echo "backup: $backup"
        ;;
    *)
        echo "usage: $(basename $0) --apply|--revert|--restore|--status"
        exit 255
        ;;
esac

