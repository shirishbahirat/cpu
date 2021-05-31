module tb_alu_control;

reg reset;
reg [152:0] idex_reg;
wire [3:0] alu_decode;

initial begin
    $from_myhdl(
        reset,
        idex_reg
    );
    $to_myhdl(
        alu_decode
    );
end

alu_control dut(
    reset,
    idex_reg,
    alu_decode
);

endmodule
