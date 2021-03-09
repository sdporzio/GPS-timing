### Components
The GPS system is comprised of:
- u-blox receiver, connected to antenna
- SBND CRT FEBm Front-End Board
- CDB, Clock Distribution Board

The u-blox receiver is also connected to a windows computer, where u-center software can be run. U-center allows information to be stored in a log file. A python script can parse that file and send diagnostic information to Grafana board.

Receiver and FEB externally powered
CDB powered via FEB

***

### Useful documentation:

- https://store.uputronics.com/files/UBX-13003221.pdf
- https://www.u-blox.com/sites/default/files/u-center_Userguide_%28UBX-13005250%29.pdf
- https://www.u-blox.com/sites/default/files/products/documents/EVK-M8T_UserGuide_%28UBX-14041540%29.pdf
- https://arxiv.org/pdf/1606.02290.pdf

***

### Notes

The antenna has to have at least 2D fix mode for correct timing, 3D better. If 2D can't be acquired, antenna has to be positioned better (outside window, outside building).

History of satellites is on diagram with flags. Green means a fix, blue means we know the satellite is out there but there's no fix.

`View->Configuration view`: to send configurations. It displays default settings, NOT current settings. To send a setting, click send after changing settings.
`View->Messages view`: let's you see and enable/disable which messages are sent to log file. `Right-click`+`Enable/Disable` to activate/disactivate information in log file.

`NMEA` format easier to parse than `UBX`, so that's what we're going to use. But timing information is in `UBX`, so we'll use `NMEA->PUBX` to get timing information.

We don't need that much information, so better to deactivate everything (`NMEA->Disable Child Messages` and `UBX->Disable Child Messages`) and basically just reactivate only `GxGSA -> GNGSA`, `GxGNS -> GNGNS` and `PUBX -> 04`. `GSA` means `GNSS and Active Satellites`, whereas `GNS` is `GNSS Fix Data`. `Gx` is code standing for the system used (`GP` for american `GPS`, `GL` for russian `GLONASS`, etc.), we're going to parse `GN` which is basically any combination of `GNSS`.

If you'll look at `View->Packet Console`, you'll see that the logger is telling you that it is sending messages for `NMEA GNGSA` and `NMEA PUBX04` to the log file. To see the actual message being sent head to `View->Text Console` (how this will effectively look in the log file).

First block of text in each line is a timestamp. Let's focus now on GNGSA (we know which line we need to look at because it starts with `$` symbol followed by `GNGSA`). It's comma separated values, so the second value after tab (should be `A`) tells us we're in automatic mode. Finally the third value after tab tells us the fix mode (should be `3` meaning 3D, `2` for 2D ok but not great, this values should be monitored for reference.).

Might be useful to get the number of satellites used, to get an idea of the quality of the fix, so we look at the eight field after tabs, for the SV number.