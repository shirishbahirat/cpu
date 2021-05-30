module tb_decode;

reg reset;
reg [63:0] ifid_reg;
wire [4:0] ra;
wire [4:0] rb;
wire [4:0] wa;
wire [6:0] opcode;

initial begin
    $from_myhdl(
        reset,
        ifid_reg
    );
    $to_myhdl(
        ra,
        rb,
        wa,
        opcode
    );
end

decode dut(
    reset,
    ifid_reg,
    ra,
    rb,
    wa,
    opcode
);

endmodule
