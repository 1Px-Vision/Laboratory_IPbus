# Laboratory_IPbus

This project implements a small IPbus/uHAL-based instrument simulation with a FIFO-style data interface and a Dash web dashboard. It can run in two modes:

1. **Mock mode**: pure Python simulation, no FPGA or IPbus server required.
2. **uHAL/IPbus mode**: communicates with an IPbus endpoint using XML connection and address-table files.

The project is useful for testing IPbus register access, FIFO write/read operations, channel-based data acquisition, and simple user-control dashboards before connecting to real FPGA firmware.

---

## Project Overview

The simulated instrument includes:

- IPbus XML connection file.
- IPbus address-table XML file.
- Register-style instrument control.
- FIFO data write/read interface.
- Simulated multi-channel ADC/sample generator.
- Dash web dashboard for user interaction.
- Bar graph showing the latest value of each simulated channel.
- CLI test script for FIFO validation.

The FIFO word format is:
```
bit[31:24] = channel ID
bit[15:0]  = sample or ADC value
```
## Running with the IPbus Dummy UDP Server

Start the dummy hardware server in one terminal:
```
/opt/cactus/bin/uhal/tests/DummyHardwareUdp.exe -p 50001 -v 2
```
