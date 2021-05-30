module tb_ifid_pipl;

reg reset;
wire [63:0] ifid_reg;
reg [31:0] instruction;
reg [31:0] pc;

initial begin
    $from_myhdl(
        reset,
        instruction,
        pc
    );
    $to_myhdl(
        ifid_reg
    );
end

ifid_pipl dut(
    reset,
    ifid_reg,
    instruction,
    pc
);

endmodule
