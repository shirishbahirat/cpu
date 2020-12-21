module tb_alu_control;

reg reset;
reg [31:0] instruction;
reg [3:0] alu_op;
wire [3:0] alu_decode;

initial begin
    $from_myhdl(
        reset,
        instruction,
        alu_op
    );
    $to_myhdl(
        alu_decode
    );
end

alu_control dut(
    reset,
    instruction,
    alu_op,
    alu_decode
);

endmodule
