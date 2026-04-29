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

## Instrument Register Map

A simplified example register map is shown below.

|      Address | Node                | Permission | Description                 |
| -----------: | ------------------- | ---------- | --------------------------- |
| `0x00000000` | `REG.ID`            | `rw`       | Instrument ID               |
| `0x00000001` | `REG.CTRL`          | `rw`       | Control register            |
| `0x00000002` | `REG.STATUS`        | `r`        | Status register             |
| `0x00000003` | `REG.CHANNEL_MASK`  | `rw`       | Channel enable mask         |
| `0x00000004` | `REG.SAMPLE_PERIOD` | `rw`       | Sample period configuration |
| `0x00000005` | `REG.NUM_CHANNELS`  | `rw`       | Number of active channels   |
| `0x00001000` | `FIFO.DATA`         | `rw`       | FIFO data port              |
| `0x00001001` | `FIFO.COUNT`        | `r`        | FIFO word count             |
| `0x00001002` | `FIFO.STATUS`       | `r`        | FIFO status flags           |

### Notes About DummyHardwareUdp

The IPbus dummy UDP server is useful for checking:

IPbus connection files.
XML address-table parsing.
Basic register read/write access.
Block read/write syntax.

However, the dummy server may behave like a simple memory model, not a true hardware FIFO. In real FPGA firmware, the FIFO data node should be connected to logic that performs:

FIFO push on write.
FIFO pop on read.
FIFO empty/full status generation.
FIFO word count tracking.

For a real FPGA design, the same XML mapping can be reused, but the firmware must implement the mapped registers and FIFO behavior.
