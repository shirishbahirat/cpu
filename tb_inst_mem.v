module tb_inst_mem;

reg reset;
reg [31:0] read_addr;
wire [31:0] instruction;

initial begin
    $from_myhdl(
        reset,
        read_addr
    );
    $to_myhdl(
        instruction
    );
end

inst_mem dut(
    reset,
    read_addr,
    instruction
);

endmodule
