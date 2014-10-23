# TRIM patcher #

Based on Grant Pannell [information](http://digitaldj.net/2011/07/21/trim-enabler-for-lion/) about how to patch
Lion properly to enable TRIM support on non-Apple branded
SSDs, here's a script that ought to make it harder to shoot
yourself in the foot.

## Important note about Yosemite ##

Yosemite now signs kexts and refuses to load unsigned ones. This means a patched version won't load, hence your Mac won't boot. If you still want to use TRIM patcher on Yosemite, you can use the following command to allow unsigned kexts to load:

    nvram boot-args=kext-dev-mode=1

This comes at a price though, as you're lowering one level of defense in your system security.

## Warning ##

I took most steps I could to ensure kitten safety, but can make no warranty.In any case you're on your own. This is ultimately a sensitive hack and you take full responsibility by running this script.

I have tested this successfully on a MacBook Pro 5,5 with Mac OS X 10.7.1 upgraded from 10.7 and a SATA-II Samsung 470 Series 128G in the HD slot. The patched file is the same as in 10.7. I later tested it on 10.7.2.

## Usage ##

Simply start up a terminal and run the script:

    python trim_patcher.py

As the kext cache gets cleared upon success you might find it seems to 
take some time to complete.

Once the script ends, reboot.

You can then check if it was taken into account via the System Profiler: go to Serial-ATA and look for "TRIM support: yes".

It is debated whether Sandforce-based SSDs (or other recent auto-GC SSDs) actually need this, both performance-wise and wear-wise.

## Available arguments ##

Run with no arguments to see a quick reminder. Here's something more extensive about what's actually done:

    apply       applies the patch, after making sure we know the
                file we're applying to, backing it up only if it's
                the original one, and subsequently checking if the
                patch applied correctly.
    restore     restores from the previously made backup.
    status      shows current situation, including status of the file
                and whether a backup is available.

In any case of changing success, the kext cache gets cleared.

## Thanks ##
 
- [Grant Pannell](http://digitaldj.net/2011/07/21/trim-enabler-for-lion/)
- [digital_dreamer](http://www.insanelymac.com/forum/index.php?s=523f85101e81849b73e6333ed420c6de&showtopic=256493&st=0&p=1680183&#entry1680183)

