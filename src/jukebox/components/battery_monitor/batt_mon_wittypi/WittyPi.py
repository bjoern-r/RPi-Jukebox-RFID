# MIT License
#
# Copyright (c) 2024 Bjoern Riemer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Contributing author(s):
# - Bjoern Riemer

from smbus import SMBus
import logging
import time

WP_I2C_ADDR = 0x08
WP_I2C_ID=0
WP_I2C_VOLTAGE_IN_I=1
WP_I2C_VOLTAGE_IN_D=2
WP_I2C_VOLTAGE_OUT_I=3
WP_I2C_VOLTAGE_OUT_D=4
WP_I2C_CURRENT_OUT_I=5
WP_I2C_CURRENT_OUT_D=6
WP_I2C_POWER_MODE=7
WP_I2C_LV_SHUTDOWN=8
WP_I2C_ALARM1_TRIGGERED=9
WP_I2C_ALARM2_TRIGGERED=10
WP_I2C_ACTION_REASON=11
WP_I2C_FW_REVISION=12

WP_I2C_LM75B_TEMPERATURE=50

logger = logging.getLogger('jb.battmon')

class WittyPi:
    # I2C communication driver for WittyPi, using only smbus2

    def __init__(self, bus=0):
        self._busnr=bus;
        self.i2c_bus=SMBus(self._busnr)
        # Check ID
        fw_id = self.get_fw_id()
        if fw_id == 55:
            print("WittyPi 4 L3V7 with FW",self.get_fw_revision(), "found")

    def get_input_voltage(self):
        i = self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_VOLTAGE_IN_I)
        d = self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_VOLTAGE_IN_D)
        res = i + float(d)/100.
        return res

    def get_power_mode(self):
        b = self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_POWER_MODE)
        return b # int 0 or 1

    def get_action_reason(self):
        b = self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_ACTION_REASON)
        return b 

    def get_output_voltage(self):
        i = self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_VOLTAGE_OUT_I)
        d = self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_VOLTAGE_OUT_D)
        return float(i) + float(d)/100.


    def get_output_current(self):
        i = self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_CURRENT_OUT_I)
        d = self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_CURRENT_OUT_D)
        return float(i) + float(d)/100.
    
    def get_fw_id(self):
        return self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_ID)

    def get_fw_revision(self):
        return self.i2c_bus.read_byte_data(WP_I2C_ADDR, WP_I2C_FW_REVISION)

    def get_temperature(self):
        d = self.i2c_bus.read_i2c_block_data(WP_I2C_ADDR, WP_I2C_LM75B_TEMPERATURE,2)
        val = ( (d[0]<<3) | (d[1]>>5) )
        if val >= 0x400:
            val = (val&0x3FF)-1024
        return val*0.125