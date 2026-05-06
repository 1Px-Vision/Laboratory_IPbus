
#!/usr/bin/env python3
 
import sys
import time
import uhal
 
 
CONNECTION_FILE = "dummy_com.xml"
DEVICE_ID = "dummy_fifo"
 
 
def read32(hw, node_name: str) -> int:
    value = hw.getNode(node_name).read()
    hw.dispatch()
    return int(value)
 
 
def write32(hw, node_name: str, value: int) -> None:
    hw.getNode(node_name).write(value)
    hw.dispatch()
 
 
def fifo_samples(status_value: int) -> int:
    return (status_value >> 16) & 0xFFFF
 
 
def print_fifo_status(hw, title: str) -> None:
    try:
        ififo_sr = read32(hw, "ififosr")
        ofifo_sr = read32(hw, "ofifosr")
 
        print(f"\n[{title}] FIFO status")
        print(f" IFIFO_SR = 0x{ififo_sr:08X} | SPSCNT = {fifo_samples(ififo_sr)}")
        print(f" OFIFO_SR = 0x{ofifo_sr:08X} | SPSCNT = {fifo_samples(ofifo_sr)}")
 
    except Exception as e:
        print("[WARNING] Could not read FIFO status.")
        print(e)
 
 
def reset_fifo(hw, cr_node: str, fifo_name: str) -> None:
    """
    Reset one FIFO using its FIFO control register.
 
    The clear bit is bit 0:
        write 1 -> clear FIFO
        write 0 -> release clear
 
    This assumes the firmware supports a pulse-style clear.
    """
    print(f"[RESET] Clearing {fifo_name} using {cr_node}")
 
    write32(hw, cr_node, 0x00000001)
    time.sleep(0.001)
    write32(hw, cr_node, 0x00000000)
    time.sleep(0.001)
 
 
def reset_all_fifos(hw) -> None:
    print("\n[RESET] Reset input and output FIFOs first")
 
    reset_fifo(hw, "ififocr", "IFIFO")
    reset_fifo(hw, "ofifocr", "OFIFO")
 
    print("[PASS] FIFO reset sequence completed.")
 
 
def main() -> int:
    try:
        uhal.setLogLevelTo(uhal.LogLevel.INFO)
    except Exception:
        pass
 
    manager = uhal.ConnectionManager(f"file://{CONNECTION_FILE}")
    hw = manager.getDevice(DEVICE_ID)
 
    print(f"[OK] Device ID : {hw.id()}")
    print(f"[OK] URI       : {hw.uri()}")
 
    # ------------------------------------------------------------
    # FIRST STEP: Reset input/output FIFOs
    # ------------------------------------------------------------
    try:
        reset_all_fifos(hw)
        print_fifo_status(hw, "AFTER RESET")
 
    except Exception as e:
        print("[FAIL] FIFO reset failed.")
        print("Check that ififocr and ofifocr have permission='rw' or permission='w' in the XML.")
        print(e)
        return 1
 
    # ------------------------------------------------------------
    # TEST 1: Basic read
    # ------------------------------------------------------------
    try:
        print("\n[TEST 1] Read ireg0")
        value = read32(hw, "ireg0")
        print(f"[PASS] ireg0 = 0x{value:08X}")
 
    except Exception as e:
        print("[FAIL] Read ireg0 failed.")
        print(e)
        return 1
 
    # ------------------------------------------------------------
    # TEST 2: Write oreg1
    # ------------------------------------------------------------
    try:
        print("\n[TEST 2] Write oreg1 = 0x00000025")
        write32(hw, "oreg1", 0x25)
        print("[PASS] Write oreg1 completed.")
 
    except Exception as e:
        print("[FAIL] Write oreg1 failed.")
        print("This usually means the target did not acknowledge the write transaction.")
        print(e)
        return 1
 
    # ------------------------------------------------------------
    # TEST 3: Read back same register oreg1
    # ------------------------------------------------------------
    try:
        print("\n[TEST 3] Read back oreg1")
        value = read32(hw, "oreg1")
        print(f"[PASS] oreg1 = 0x{value:08X}")
 
        if value == 0x25:
            print("[PASS] oreg1 readback matches written value.")
        else:
            print("[WARNING] oreg1 readback does not match written value.")
 
    except Exception as e:
        print("[FAIL] Readback oreg1 failed.")
        print(e)
        return 1
 
    # ------------------------------------------------------------
    # TEST 4: Read ireg1
    # ------------------------------------------------------------
    try:
        print("\n[TEST 4] Read ireg1")
        value = read32(hw, "ireg1")
        print(f"[INFO] ireg1 = 0x{value:08X}")
        print("[INFO] ireg1 will only change if firmware connects oreg1 -> ireg1.")
 
    except Exception as e:
        print("[FAIL] Read ireg1 failed.")
        print(e)
        return 1
 
    # ------------------------------------------------------------
    # TEST 5: Normal register 32-bit diagnostic
    # ------------------------------------------------------------
    try:
        print("\n[TEST 5] Normal register 32-bit diagnostic")
 
        patterns = [
            0x12345678,
            0xCAFE0001,
            0xDEADBEEF,
            0xFFFFFFFF,
        ]
 
        for tx in patterns:
            write32(hw, "oreg1", tx)
            rx = read32(hw, "oreg1")
 
            print(f"TX=0x{tx:08X} RX=0x{rx:08X}")
 
            if rx == tx:
                print(" [OK] 32-bit register readback correct.")
            else:
                print(" [FAIL] 32-bit register readback mismatch.")
 
    except Exception as e:
        print("[FAIL] Normal register 32-bit diagnostic failed.")
        print(e)
        return 1
 
    # ------------------------------------------------------------
    # RESET AGAIN BEFORE FIFO DATA TEST
    # ------------------------------------------------------------
    try:
        print("\n[RESET] Reset FIFOs again before OFIFO/IFIFO diagnostic")
        reset_all_fifos(hw)
        print_fifo_status(hw, "BEFORE FIFO TEST")
 
    except Exception as e:
        print("[FAIL] FIFO reset before data-width diagnostic failed.")
        print(e)
        return 1
 
    # ------------------------------------------------------------
    # TEST 6: OFIFO data-width diagnostic
    # ------------------------------------------------------------
    try:
        print("\n[TEST 6] OFIFO data-width diagnostic")
 
        patterns = [
            0x00000000,
            0x00000001,
            0x0000000A,
            0x0000CAFE,
            0x0000FFFF,
            0x12345678,
            0xCAFE0001,
            0xDEADBEEF,
            0xFFFF0000,
            0xFFFFFFFF,
        ]
 
        for tx in patterns:
            write32(hw, "ofifo", tx)
 
            # Small delay only if the firmware internally loops OFIFO -> IFIFO.
            time.sleep(0.001)
 
            reg_tx = read32(hw, "ofifo")
            rx = read32(hw, "ififo")
 
            print(
                f"TX=0x{tx:08X} "
                f"Reg_TX=0x{reg_tx:08X} "
                f"RX=0x{rx:08X}"
            )
 
            if rx == tx:
                print(" [OK] OFIFO preserves full 32-bit data.")
            elif rx == (tx & 0xFFFF):
                print(" [WARNING] OFIFO appears to preserve only lower 16 bits.")
            else:
                print(" [INFO] OFIFO readback has custom/non-register behavior.")
 
        print_fifo_status(hw, "AFTER FIFO TEST")
 
    except Exception as e:
        print("[FAIL] OFIFO data-width diagnostic failed.")
        print(e)
        return 1
 
    print("\n[PASS] All tests completed.")
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())
