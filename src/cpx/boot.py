'Allow file system write access if switch is moved to the right'

import board
import digitalio
import storage

switch = digitalio.DigitalInOut(board.D7)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP
storage.remount("/", switch.value)
