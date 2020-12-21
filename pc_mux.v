// File: pc_mux.v
// Generated by MyHDL 0.11
// Date: Sun Dec 20 17:30:45 2020


`timescale 1ns/10ps

module pc_mux (
    reset,
    pc,
    pc_addr,
    jmp_addr,
    pc_sel
);


input reset;
output [31:0] pc;
reg [31:0] pc;
input [31:0] pc_addr;
input [31:0] jmp_addr;
input [0:0] pc_sel;




always @(jmp_addr, reset, pc_addr, pc_sel) begin: PC_MUX_PMUX
    if ((reset == 1)) begin
        if (pc_sel) begin
            pc = jmp_addr;
        end
        else begin
            pc = pc_addr;
        end
    end
end

endmodule