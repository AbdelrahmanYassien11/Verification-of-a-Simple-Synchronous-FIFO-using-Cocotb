module fifo (
    input wire clk,
    input wire reset,
    input wire wr_en,
    input wire rd_en,
    input wire [7:0] data_in,
    output reg [7:0] data_out,
    output reg full,
    output reg empty
);

    reg [7:0] fifo_mem [3:0]; // 4-deep FIFO
    reg [1:0] write_ptr;
    reg [1:0] read_ptr;
    reg [2:0] count; // To keep track of number of elements

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            write_ptr <= 2'b00;
            read_ptr <= 2'b00;
            count <= 3'b000;
            full <= 1'b0;
            empty <= 1'b1;
        end else begin
            // Write operation
            if (wr_en && !full) begin
                fifo_mem[write_ptr] <= data_in;
                write_ptr <= write_ptr + 1;
                count <= count + 1;
            end

            // Read operation
            if (rd_en && !empty) begin
                data_out <= fifo_mem[read_ptr];
                read_ptr <= read_ptr + 1;
                count <= count - 1;
            end

            // Update full and empty flags
            full <= (count == 3'b100);
            empty <= (count == 3'b000);
        end
    end
endmodule