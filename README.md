# TRIM patcher #

Based on Grant Pannell [information](http://digitaldj.net/2011/07/21/trim-enabler-for-lion/) about how to patch
Lion properly to enable TRIM support on non-Apple branded
SSDs, here's a script that ought to make it harder to shoot
yourself in the foot.

## Warning ##

I took most steps I could to ensure kitten safety, but can make no warranty.
I have tested this successfully on a MacBook Pro 5,5 with Mac OS X 10.7.1 and a SATA-II Samsung 470 Series 128G in the HD slot. The patched file is the same as in 10.7.0.

## Usage ##

Simply start up a terminal and run the script.
As the kext cache gets cleared upon success you might find it seems to 
take some time to complete.

Once the script ends (no output means success), reboot.

You can then check if it was taken into account via the System Profiler: go to Serial-ATA and look for "TRIM support: yes".

It is debated whether Sandforce-based SSDs (or other auto-GC SSDs) actually need this.

## Available arguments ##

Run with no arguments to see a quick reminder. Here's something more extensive about what's actually done:

    --apply     applies the patch, after making sure we know the
                file we're applying to, backing it up only if it's
                the original one, and subsequently checking if the
                patch applied correctly.
    --revert    reverts the patch, after making sure we're working
                on the patched file, and afterward checks for correct
                reversion.
    --restore   restores from the previously made backup.
    --status    shows current situation, including status of the file
                and whether a backup is available.

In any case of success, the kext cache gets cleared.

## Thanks ##
 
- [Grant Pannell](http://digitaldj.net/2011/07/21/trim-enabler-for-lion/)
- [digital_dreamer](http://www.insanelymac.com/forum/index.php?s=523f85101e81849b73e6333ed420c6de&showtopic=256493&st=0&p=1680183&#entry1680183)

