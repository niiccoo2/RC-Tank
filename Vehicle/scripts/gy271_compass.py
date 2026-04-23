#!/usr/bin/env python3
import math
import time
from typing import Any, Dict, Optional, Tuple

import smbus  # type: ignore


class CompassError(Exception):
    pass


class GY271Compass:
    """Auto-detect driver for common GY-271 magnetometer variants.

    Supported register maps:
    - QMC5883L / QMC5883P-like (addresses 0x0D or 0x2C)
    - HMC5883L-like (address 0x1E)
    """

    DEFAULT_ADDRESSES = (0x2C, 0x0D, 0x1E)

    def __init__(
        self,
        bus_number: int = 7,
        address: Optional[int] = None,
        declination_deg: float = 0.0,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
    ):
        self.bus_number = bus_number
        self.bus = smbus.SMBus(bus_number)
        self.address: int = address if address is not None else self._find_address()
        self.declination_deg = declination_deg
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.protocol = ""
        self.detection_warning: Optional[str] = None
        self._last_sample: Optional[Tuple[int, int, int]] = None

        self.protocol = self._detect_and_configure()

    def _find_address(self) -> int:
        for addr in self.DEFAULT_ADDRESSES:
            try:
                self.bus.read_byte_data(addr, 0x00)
                return addr
            except OSError:
                continue
        raise CompassError(
            f"No known GY-271 address found on bus {self.bus_number}. "
            f"Checked: {', '.join(hex(a) for a in self.DEFAULT_ADDRESSES)}"
        )

    def _detect_and_configure(self) -> str:
        protocols = ["qmc", "qmc_rev", "hmc"]
        if self.address == 0x1E:
            protocols = ["hmc", "qmc", "qmc_rev"]

        best_proto: Optional[str] = None
        best_score = -999

        for proto in protocols:
            try:
                if proto in ("qmc", "qmc_rev"):
                    self._configure_qmc()
                else:
                    self._configure_hmc()

                score = self._probe_signal(proto, samples=8, delay_s=0.04)
                if score > best_score:
                    best_score = score
                    best_proto = proto
            except OSError:
                continue

        if best_proto is None:
            raise CompassError(
                f"Could not initialize a supported protocol at address {hex(self.address)} on bus {self.bus_number}."
            )

        if best_score <= 0:
            self.detection_warning = (
                "Compass protocol selected with weak confidence. "
                "If heading is stuck, chip/register map may be different."
            )

        return best_proto

    def _configure_qmc(self) -> None:
        # Set/reset period register
        self.bus.write_byte_data(self.address, 0x0B, 0x01)
        # Continuous mode, ODR=200Hz, range=8G, OSR=512
        self.bus.write_byte_data(self.address, 0x09, 0x1D)
        # Disable interrupt/rollover reset bits
        self.bus.write_byte_data(self.address, 0x0A, 0x00)

    def _configure_hmc(self) -> None:
        # 8-average, 15 Hz normal mode
        self.bus.write_byte_data(self.address, 0x00, 0x70)
        # Gain config
        self.bus.write_byte_data(self.address, 0x01, 0x20)
        # Continuous measurement mode
        self.bus.write_byte_data(self.address, 0x02, 0x00)

    def _probe_signal(self, proto: str, samples: int, delay_s: float) -> int:
        seen = set()
        for _ in range(samples):
            xyz = self._read_xyz(proto)
            seen.add(xyz)
            time.sleep(delay_s)

        score = len(seen)
        if (128, 0, 0) in seen:
            score -= 5
        if (0, 0, 0) in seen:
            score -= 3
        return score

    @staticmethod
    def _to_int16(lsb: int, msb: int) -> int:
        value = (msb << 8) | lsb
        if value & 0x8000:
            value -= 0x10000
        return value

    def _read_xyz(self, proto: str) -> Tuple[int, int, int]:
        if proto == "qmc":
            data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
            x = self._to_int16(data[0], data[1])
            y = self._to_int16(data[2], data[3])
            z = self._to_int16(data[4], data[5])
            return x, y, z

        if proto == "qmc_rev":
            data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
            x = self._to_int16(data[1], data[0])
            y = self._to_int16(data[3], data[2])
            z = self._to_int16(data[5], data[4])
            return x, y, z

        # HMC register order: X, Z, Y as big-endian pairs starting at 0x03
        data = self.bus.read_i2c_block_data(self.address, 0x03, 6)
        x = self._to_int16(data[1], data[0])
        z = self._to_int16(data[3], data[2])
        y = self._to_int16(data[5], data[4])
        return x, y, z

    def read(self) -> Dict[str, Any]:
        x_raw, y_raw, z_raw = self._read_xyz(self.protocol)
        x = x_raw - self.x_offset
        y = y_raw - self.y_offset

        heading = (math.degrees(math.atan2(y, x)) + self.declination_deg + 360.0) % 360.0

        self._last_sample = (x_raw, y_raw, z_raw)
        return {
            "heading": heading,
            "x": float(x_raw),
            "y": float(y_raw),
            "z": float(z_raw),
            "protocol": self.protocol,
            "address": float(self.address),
            "bus": float(self.bus_number),
        }
