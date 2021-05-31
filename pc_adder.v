// File: pc_adder.v
// Generated by MyHDL 0.11
// Date: Mon May 31 10:48:30 2021


`timescale 1ns/10ps

module pc_adder (
    reset,
    clk,
    pc,
    pc_next
);


input reset;
input [0:0] clk;
input [31:0] pc;
output [31:0] pc_next;
reg [31:0] pc_next;




always @(posedge clk) begin: PC_ADDER_PADDER
    if ((reset == 1)) begin
        pc_next <= (pc + 1);
    end
end

endmodule
