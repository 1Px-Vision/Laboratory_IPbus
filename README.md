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

# uHAL Dummy FIFO Address Table

This repository contains a simple XML address table for testing a dummy FIFO/register firmware block using `uHAL`. The design exposes input registers, output registers, and input/output FIFO interfaces through a memory-mapped IPbus address space.

## Address Map Overview

The address table defines three main groups:

1. **Input registers**: read-only registers `ireg0` to `ireg15`
2. **Output registers**: read/write registers `oreg0` to `oreg15`
3. **FIFO interfaces**: input FIFO, output FIFO, control registers, and status registers

## Register Map

### Input Registers

The input registers are read-only and are mapped from address `0x80010000` to `0x8001003C`.

| Register | Address | Access | Description |
|---|---:|---|---|
| `ireg0`  | `0x80010000` | Read-only | Input register 0 |
| `ireg1`  | `0x80010004` | Read-only | Input register 1 |
| `ireg2`  | `0x80010008` | Read-only | Input register 2 |
| `ireg3`  | `0x8001000C` | Read-only | Input register 3 |
| `ireg4`  | `0x80010010` | Read-only | Input register 4 |
| `ireg5`  | `0x80010014` | Read-only | Input register 5 |
| `ireg6`  | `0x80010018` | Read-only | Input register 6 |
| `ireg7`  | `0x8001001C` | Read-only | Input register 7 |
| `ireg8`  | `0x80010020` | Read-only | Input register 8 |
| `ireg9`  | `0x80010024` | Read-only | Input register 9 |
| `ireg10` | `0x80010028` | Read-only | Input register 10 |
| `ireg11` | `0x8001002C` | Read-only | Input register 11 |
| `ireg12` | `0x80010030` | Read-only | Input register 12 |
| `ireg13` | `0x80010034` | Read-only | Input register 13 |
| `ireg14` | `0x80010038` | Read-only | Input register 14 |
| `ireg15` | `0x8001003C` | Read-only | Input register 15 |

### Output Registers

The output registers are read/write and are mapped from address `0x80010040` to `0x8001007C`.

| Register | Address | Access | Description |
|---|---:|---|---|
| `oreg0`  | `0x80010040` | Read/write | Output register 0 |
| `oreg1`  | `0x80010044` | Read/write | Output register 1 |
| `oreg2`  | `0x80010048` | Read/write | Output register 2 |
| `oreg3`  | `0x8001004C` | Read/write | Output register 3 |
| `oreg4`  | `0x80010050` | Read/write | Output register 4 |
| `oreg5`  | `0x80010054` | Read/write | Output register 5 |
| `oreg6`  | `0x80010058` | Read/write | Output register 6 |
| `oreg7`  | `0x8001005C` | Read/write | Output register 7 |
| `oreg8`  | `0x80010060` | Read/write | Output register 8 |
| `oreg9`  | `0x80010064` | Read/write | Output register 9 |
| `oreg10` | `0x80010068` | Read/write | Output register 10 |
| `oreg11` | `0x8001006C` | Read/write | Output register 11 |
| `oreg12` | `0x80010070` | Read/write | Output register 12 |
| `oreg13` | `0x80010074` | Read/write | Output register 13 |
| `oreg14` | `0x80010078` | Read/write | Output register 14 |
| `oreg15` | `0x8001007C` | Read/write | Output register 15 |

## FIFO Interface

The design includes one input FIFO and one output FIFO. Both FIFOs use non-incremental access mode, which means repeated reads or writes target the same FIFO data port address.

| Node | Address | Access | Mode | Description |
|---|---:|---|---|---|
| `ififo` | `0x80010080` | Read-only | Non-incremental | Input FIFO data port |
| `ififocr` | `0x80010084` | Read/write | Single | Input FIFO control register |
| `ififosr` | `0x80010088` | Read-only | Single | Input FIFO status register |
| `ofifo` | `0x80010090` | Read/write | Non-incremental | Output FIFO data port |
| `ofifocr` | `0x80010094` | Read/write | Single | Output FIFO control register |
| `ofifosr` | `0x80010098` | Read-only | Single | Output FIFO status register |

## FIFO Control Registers

The FIFO control registers contain a clear bit used to reset the FIFO contents.

| Register | Bit Mask | Field | Description |
|---|---:|---|---|
| `ififocr` | `0x00000001` | `CLR` | Clear input FIFO |
| `ofifocr` | `0x00000001` | `CLR` | Clear output FIFO |

A typical FIFO reset sequence is:

```python
hw.getNode("ififocr").write(0x1)
hw.dispatch()
hw.getNode("ififocr").write(0x0)
hw.dispatch()

hw.getNode("ofifocr").write(0x1)
hw.dispatch()
hw.getNode("ofifocr").write(0x0)
hw.dispatch()

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

* FIFO data ports use mode="non-incremental" because multiple accesses must target the same hardware FIFO address.
* FIFO control registers must be writable; ififocr and ofifocr should use permission="rw".
* The FIFO status counters are stored in the upper 16 bits of the status register.
* The output FIFO status field descriptions should refer to AFULL as almost full and FULL as full.
* Register readback from oreg nodes depends on firmware support for readable output registers.
* Reading ififo after writing ofifo only works if the firmware connects or loops the output FIFO to the input FIFO.
