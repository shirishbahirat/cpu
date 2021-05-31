module tb_idex_pipl;

reg reset;
wire [120:0] idex_reg;
reg [31:0] instruction;
reg [31:0] pc;

initial begin
    $from_myhdl(
        reset,
        instruction,
        pc
    );
    $to_myhdl(
        idex_reg
    );
end

idex_pipl dut(
    reset,
    idex_reg,
    instruction,
    pc
);

endmodule
