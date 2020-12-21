module tb_alu_mux;

reg reset;
reg [31:0] im_gen;
reg [31:0] rdb;
wire [31:0] rdx;
reg [0:0] alu_src;

initial begin
    $from_myhdl(
        reset,
        im_gen,
        rdb,
        alu_src
    );
    $to_myhdl(
        rdx
    );
end

alu_mux dut(
    reset,
    im_gen,
    rdb,
    rdx,
    alu_src
);

endmodule
