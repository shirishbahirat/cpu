module tb_control;

reg reset;
reg [6:0] opcode;
wire [0:0] brnch;
wire [0:0] mem_rd;
wire [0:0] mem_to_rgs;
wire [3:0] alu_op;
wire [0:0] mem_wr;
wire [0:0] alu_src;
wire [0:0] reg_wr;

initial begin
    $from_myhdl(
        reset,
        opcode
    );
    $to_myhdl(
        brnch,
        mem_rd,
        mem_to_rgs,
        alu_op,
        mem_wr,
        alu_src,
        reg_wr
    );
end

control dut(
    reset,
    opcode,
    brnch,
    mem_rd,
    mem_to_rgs,
    alu_op,
    mem_wr,
    alu_src,
    reg_wr
);

endmodule
