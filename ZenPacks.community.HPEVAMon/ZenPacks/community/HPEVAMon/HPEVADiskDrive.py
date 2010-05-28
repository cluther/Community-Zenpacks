################################################################################
#
# This program is part of the HPEVAMon Zenpack for Zenoss.
# Copyright (C) 2010 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""HPEVADiskDrive

HPEVADiskDrive is an abstraction of a harddisk.

$Id: HPEVADiskDrive.py,v 1.1 2010/05/14 18:09:18 egor Exp $"""

__version__ = "$Revision: 1.1 $"[11:-2]

from Globals import DTMLFile, InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ZenModel.HWComponent import *
from Products.ZenModel.HardDisk import *
from Products.ZenRelations.RelSchema import *
from Products.ZenModel.ZenossSecurity import *
from HPEVAComponent import *
from Products.ZenUtils.Utils import convToUnits

import logging
log = logging.getLogger("zen.HPEVADiskDrive")


class HPEVADiskDrive(HardDisk, HPEVAComponent):
    """HPDiskDrive object"""

    portal_type = meta_type = 'HPEVADiskDrive'

    size = 0
    diskType = ""
    hotPlug = 0
    bay = 0
    FWRev = ""
    wwn = ""

    _properties = HWComponent._properties + (
                 {'id':'description', 'type':'string', 'mode':'w'},
                 {'id':'hostresindex', 'type':'int', 'mode':'w'},
                 {'id':'diskType', 'type':'string', 'mode':'w'},
                 {'id':'hotPlug', 'type':'boolean', 'mode':'w'},
                 {'id':'size', 'type':'int', 'mode':'w'},
                 {'id':'bay', 'type':'int', 'mode':'w'},
                 {'id':'FWRev', 'type':'string', 'mode':'w'},
                 {'id':'wwn', 'type':'string', 'mode':'w'},
                )    

    _relations = HWComponent._relations + (
        ("hw", ToOne(ToManyCont,
                            "ZenPacks.community.HPEVAMon.HPEVADeviceHW",
                            "harddisks")),
        ("enclosure", ToOne(ToMany,
                            "ZenPacks.community.HPEVAMon.HPEVAStorageDiskEnclosure",
                            "harddisks")),
        ("storagepool", ToOne(ToMany,
                            "ZenPacks.community.HPEVAMon.HPEVAStoragePool",
                            "harddisks")),
        )



    factory_type_information = ( 
        { 
            'id'             : 'DiskDrive',
            'meta_type'      : 'DiskDrive',
            'description'    : """Arbitrary device grouping class""",
            'icon'           : 'DiskDrive_icon.gif',
            'product'        : 'HPEVAMon',
            'factory'        : 'manage_addHardDisk',
            'immediate_view' : 'viewHPEVADiskDrive',
            'actions'        :
            ( 
                { 'id'            : 'status'
                , 'name'          : 'Status'
                , 'action'        : 'viewHPEVADiskDrive'
                , 'permissions'   : (ZEN_VIEW,)
                },
                { 'id'            : 'events'
                , 'name'          : 'Events'
                , 'action'        : 'viewEvents'
                , 'permissions'   : (ZEN_VIEW, )
                },
                { 'id'            : 'perfConf'
                , 'name'          : 'Template'
                , 'action'        : 'objTemplates'
                , 'permissions'   : ("Change Device", )
                },
                { 'id'            : 'viewHistory'
                , 'name'          : 'Modifications'
                , 'action'        : 'viewHistory'
                , 'permissions'   : (ZEN_VIEW_MODIFICATIONS,)
                },
            )
          },
        )

    security = ClassSecurityInfo()

    security.declareProtected('Change Device', 'setEnclosure')
    def setEnclosure(self, encid):
        """
        Set the enclosure relationship to the enclosure specified by the given
        id.
        """
        encl = None
        for enclosure in self.hw().enclosures():
            if str(enclosure.id) != str(encid): continue
            encl = enclosure
            break
        if encl: self.enclosure.addRelation(encl)
        else: log.warn("enclosure id:%s not found", encid)

    security.declareProtected('View', 'getEnclosure')
    def getEnclosure(self):
        try: return self.enclosure()
        except: return None

    security.declareProtected('Change Device', 'setStoragePool')
    def setStoragePool(self, spid):
        """
        Set the storagepool relationship to the storage pool specified by the given
        id.
        """
        strpool = None
        for storagepool in self.device().os.storagepools():
            if storagepool.caption != spid: continue
            strpool = storagepool
            break
        if strpool: self.storagepool.addRelation(strpool)
        else: log.warn("storage pool id:%s not found", spid)

    security.declareProtected('View', 'getStoragePool')
    def getStoragePool(self):
        try: return self.storagepool()
        except: return None

    def getEnclosureName(self):
        return self.getEnclosure() and self.getEnclosure().id or 'Unknown'

    def diskImg(self):
        return '/zport/dmd/hpevadisk_%s_%s'%(
                self.diskType.startswith('online') and 'online' or 'nearonline',
                self.statusDot())

    def getStatus(self):
        """
        Return the components status
        """
        return int(round(self.cacheRRDValue('OperationalStatus', 0)))

    def bayString(self):
        return '%s bay %02d'%(self.getEnclosureName() ,int(self.bay))

    def sizeString(self):
        """
        Return the number of total bytes in human readable form ie 10MB
        """
        return convToUnits(self.size,divby=1000)

    def rpmString(self):
        """
        Return the RPM in tradition form ie 7200, 10K
        """
        return 'Unknown'

    def hotPlugString(self):
        """
        Return the HotPlug Status
        """
        if self.hotPlug: return 'Hot Swappable'
        else: return 'Non-Hot Swappable'

InitializeClass(HPEVADiskDrive)