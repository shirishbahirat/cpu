module tb_imm_gen;

reg reset;
reg [63:0] ifid_reg;
wire [31:0] im_gen;
reg [19:0] padz;
reg [19:0] padx;

initial begin
    $from_myhdl(
        reset,
        ifid_reg,
        padz,
        padx
    );
    $to_myhdl(
        im_gen
    );
end

imm_gen dut(
    reset,
    ifid_reg,
    im_gen,
    padz,
    padx
);

endmodule
