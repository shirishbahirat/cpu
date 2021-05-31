module tb_alu;

reg reset;
reg [3:0] alu_decode;
reg [152:0] idex_reg;
reg [31:0] rdx;
wire [31:0] result;

initial begin
    $from_myhdl(
        reset,
        alu_decode,
        idex_reg,
        rdx
    );
    $to_myhdl(
        result
    );
end

alu dut(
    reset,
    alu_decode,
    idex_reg,
    rdx,
    result
);

endmodule
