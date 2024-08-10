
import cocotb
import logging
from cocotb.regression import TestFactory
from cocotb.utils import get_sim_time
from cocotb.triggers import RisingEdge, FallingEdge, Timer
import queue

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cocotb.log.info("Logger is set up and should print messages.")


data_to_write_read = queue.Queue(maxsize=4)

expected_data_out = None
expected_empty = None
expected_full = None

def verilog_value_to_python(value):
    """Convert Verilog 'x' or 'z' to Python None."""
    if value == 'x' or value == 'z':
        return None
    return int(value)


async def generate_clock(dut):

    for cycle in range(200):
        dut.clk.value = 0
        await Timer(1, units="ns")
        dut.clk.value = 1
        await Timer (1, units="ns")


def output_checker(iexpected_data_out, iexpected_empty, iexpected_full, iactual_data_out, iactual_empty, iactual_full):
        # cocotb.log.info(f"[expected_data_out = {expected_data_out}]")
        # cocotb.log.info(f"[expected_empty = {expected_data_out}]")
        # cocotb.log.info(f"[expected_full = {expected_data_out}]")
        if not ((iexpected_data_out == iactual_data_out ) and 
                (iexpected_empty == iactual_empty) and 
                (iexpected_full == iactual_full)): 
            logger.error(
                    f"Failed: Expected data_out = {iexpected_data_out} when actual_data_out = {iactual_data_out}, "
                    f" expected_empty = {iexpected_empty} when actual_empty = {iactual_empty}, "
                    f" expected_full = {iexpected_full} when actual_full = {iactual_full}"                       
                    )


def expected_values(ireset, iwr_en, ird_en, idata_in):
    global expected_data_out, expected_empty, expected_full
    # cocotb.log.info(f"[reset = {ireset}]")
    # cocotb.log.info(f"[wr_en = {iwr_en}]")
    # cocotb.log.info(f"[rd_en = {ird_en}]")
    # cocotb.log.info(f"[data_out = {idata_in}]")
    if(ireset == 1):
        expected_data_out = 0 
        expected_empty    = 1
        expected_full     = 0
        write_pointer     = 0
        read_pointer      = 0
    elif((iwr_en == 1) and (ird_en == 0)):
        if not (data_to_write_read.full()):
            data_to_write_read.put(idata_in)
        flags_()
    elif((ird_en == 1) and (iwr_en == 0)):
        if not (data_to_write_read.empty()):
            expected_data_out = data_to_write_read.get();
        flags_()
    # cocotb.log.info(f"[expected_data_out = {expected_data_out}]")
    # cocotb.log.info(f"[expected_empty = {expected_data_out}]")
    # cocotb.log.info(f"[expected_full = {expected_data_out}]")


def flags_():
    global expected_empty, expected_full
    if(data_to_write_read.empty()):
        expected_empty = 1
        expected_full = 0
    elif(data_to_write_read.full()):
        expected_empty = 0
        expected_full = 1
    else:
        expected_empty = 0
        expected_full = 0


async def reset_dut (dut):
    await Timer(5, units ="ns")
    dut.reset.value = 1
    await Timer(5, units ="ns")
    expected_values(dut.reset.value, dut.wr_en.value, dut.rd_en.value, dut.data_in.value)
    output_checker(expected_data_out, expected_empty, expected_full, dut.data_out.value, dut.empty.value, dut.full.value)
    dut.reset.value = 0

async def write_dut (dut):
    await FallingEdge(dut.clk)
    dut.wr_en.value = 1
    dut.rd_en.value = 0
    dut.data_in.value = 99
    await FallingEdge(dut.clk)
    expected_values(dut.reset.value, dut.wr_en.value, dut.rd_en.value, dut.data_in.value)
    output_checker(expected_data_out, expected_empty, expected_full, dut.data_out.value, dut.empty.value, dut.full.value)


async def read_dut (dut):
    await FallingEdge(dut.clk)
    dut.wr_en.value = 0
    dut.rd_en.value = 1
    await FallingEdge(dut.clk)
    expected_values(dut.reset.value, dut.wr_en.value, dut.rd_en.value, dut.data_in.value)
    output_checker(expected_data_out, expected_empty, expected_full, dut.data_out.value, dut.empty.value, dut.full.value)





@cocotb.test()
async def fifo_test(dut):

    await cocotb.start(generate_clock(dut))


    await reset_dut(dut)

    await write_dut(dut)

    await read_dut(dut)






