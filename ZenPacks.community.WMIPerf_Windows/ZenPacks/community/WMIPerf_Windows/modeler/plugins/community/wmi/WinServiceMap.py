################################################################################
#
# This program is part of the WMIPerf_Windows Zenpack for Zenoss.
# Copyright (C) 2010 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__ = """WinServiceMap

WinServiceMap gathers status of Windows services

$Id: WinServiceMap.py,v 1.1 2010/07/23 00:09:57 egor Exp $"""

__version__ = '$Revision: 1.0 $'[11:-2]


from ZenPacks.community.WMIDataSource.WMIPlugin import WMIPlugin
from Products.ZenUtils.Utils import prepId

class WinServiceMap(WMIPlugin):

    maptype = "WinServiceMap"
    compname = "os"
    relname = "winservices"
    modname = "Products.ZenModel.WinService"

    tables = {
            "Win32_Service":
                (
                "Win32_Service",
                None,
                "root/cimv2",
                    {
                    'AcceptPause':'acceptPause',
                    'AcceptStop':'acceptStop',
                    'Caption':'_description',
                    'Name':'_name',
                    'PathName':'pathName',
                    'ServiceType':'serviceType',
                    'StartMode':'startMode',
                    'StartName':'startName',
                    'State':'_state',
                    }
                ),
            }


    def process(self, device, results, log):
        """Collect win service info from this device.
        """
        log.info('Processing WinServices for device %s' % device.id)
        instances = results.get("Win32_Service", None)
        if not instances: return
        rm = self.relMap()
        for instance in instances:
            om = self.objectMap(instance)
            om.id = prepId(om._name)
            om.setServiceClass = {'name':om._name, 'description':om._description}
            rm.append(om)
        return rm

