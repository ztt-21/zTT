import Monsoon.HVPM as HVPM
import Monsoon.sampleEngine as sampleEngine
import Monsoon.Operations as op

Mon = HVPM.Monsoon()
Mon.setup_usb()

Mon.setVout(3.85)
