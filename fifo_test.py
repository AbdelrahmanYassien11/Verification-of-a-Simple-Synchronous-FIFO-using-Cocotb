
import cocotb
import logging
from cocotb.regression import TestFactory
from cocotb.utils import get_sim_time
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.regression import random
import queue

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cocotb.log.info("Logger is set up and should print messages.")


data_to_write_read = queue.Queue(maxsize=8)

expected_data_out = None
expected_empty = None
expected_full = None

count = 0

randomized_tests = random.randint(8, 12)

def verilog_value_to_python(value):
    """Convert Verilog 'x' or 'z' to Python None."""
    if value == 'x' or value == 'z':
        return None
    return int(value)


def generate_constrained_data_in():
    global count
    while count == 0:
        data = random.randint(0, 128)  # 4-bit data range (0 to 15)
        if data == 128:  # Constraint: Data must be even
            count++;
            return data
        elif data == 0:
            count++;
            return data
    data = random.randint(0, 128)
    return data

# def randomize_operation():
#     while operation_count <= 9:
#         operation = random.randint(0,1)
#         if(operation == 0):
#             operation++;
#             return write_dut()
#     while operation_count <= 18:
#         operation = random.randint(0,1)
#         if(operation == 1):
#             operation++;
#             return read_dut()
#     operation = random.randint(0,1)
#     if(operation == 0):
#         return write_dut()
#     else:
#         return read_dut()





    global count
    while count == 0:
        data = random.randint(0, 128)  # 4-bit data range (0 to 15)
        if data == 128:  # Constraint: Data must be even
            count++;
            return data
        elif data == 0:
            count++;
            return data

    data = random.randint(0, 128)
    return data



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
        if not (iexpected_data_out == iactual_data_out ):
            cocotb.log.info(f"[Failed: Time = {get_sim_time()} expected data_out = {iexpected_data_out} when actual_data_out = {iactual_data_out}]") 
        if not (iexpected_empty == iactual_empty):
            cocotb.log.info(f"[Failed: Time = {get_sim_time()} expected_empty = {iexpected_empty} when actual_empty = {iactual_empty}]")
        if not (iexpected_full == iactual_full): 
            cocotb.log.info(f"[Failed: Time = {get_sim_time()} expected_full = {iexpected_full} when actual_full = {iactual_full}]")
                     


def expected_values(irst_n, iwr_en, ird_en, idata_in):
    global expected_data_out, expected_empty, expected_full
    # cocotb.log.info(f"[reset = {ireset}]")
    # cocotb.log.info(f"[wr_en = {iwr_en}]")
    # cocotb.log.info(f"[rd_en = {ird_en}]")
    # cocotb.log.info(f"[data_out = {idata_in}]")
    if(irst_n == 0):
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
            expected_data_out = data_to_write_read.get()
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
    dut.rst_n.value = 0
    await Timer(5, units ="ns")
    cocotb.log.info(f"[reset_dut: Time = {get_sim_time()}  rst_n = {dut.rst_n.value}]")
    expected_values(dut.rst_n.value, dut.wr_en.value, dut.rd_en.value, dut.data_in.value)
    output_checker(expected_data_out, expected_empty, expected_full, dut.data_out.value, dut.empty.value, dut.full.value)
    dut.rst_n.value = 1

async def write_dut (dut):
    cocotb.log.info(f"[write_dut: Time = {get_sim_time()}]")
    await FallingEdge(dut.clk)
    dut.wr_en.value = 1
    dut.rd_en.value = 0
    dut.data_in.value = generate_constrained_data_in()
    await FallingEdge(dut.clk)
    cocotb.log.info(f"[reset_dut: Time = {get_sim_time()}  rst_n = {dut.rst_n.value}  wr_en = {dut.wr_en.value}  rd_en = {dut.rd_en.value}  data_in = {dut.data_in.value}]")
    expected_values(dut.rst_n.value, dut.wr_en.value, dut.rd_en.value, dut.data_in.value)
    output_checker(expected_data_out, expected_empty, expected_full, dut.data_out.value, dut.empty.value, dut.full.value)
    dut.wr_en.value = 0


async def read_dut (dut):
    cocotb.log.info(f"[read_dut: Time = {get_sim_time()}]")
    await FallingEdge(dut.clk)
    dut.wr_en.value = 0
    dut.rd_en.value = 1
    await FallingEdge(dut.clk)
    cocotb.log.info(f"[reset_dut: Time = {get_sim_time()}  rst_n = {dut.rst_n.value}  wr_en = {dut.wr_en.value}  rd_en = {dut.rd_en.value}  data_in = {dut.data_in.value}]")
    expected_values(dut.rst_n.value, dut.wr_en.value, dut.rd_en.value, dut.data_in.value)
    output_checker(expected_data_out, expected_empty, expected_full, dut.data_out.value, dut.empty.value, dut.full.value)
    dut.rd_en.value = 0





@cocotb.test()
async def fifo_test(dut):

    await cocotb.start(generate_clock(dut))


    await reset_dut(dut)

    for cycle in range(randomized_tests):
        await write_dut(dut)

    for cycle in range(randomized_tests):
        await read_dut(dut)






