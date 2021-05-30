module tb_reg_file;

reg reset;
reg [0:0] clk;
reg [4:0] ra;
reg [4:0] rb;
reg [4:0] wa;
reg [31:0] wda;
reg [0:0] reg_wr;
wire [31:0] rda;
wire [31:0] rdb;

initial begin
    $from_myhdl(
        reset,
        clk,
        ra,
        rb,
        wa,
        wda,
        reg_wr
    );
    $to_myhdl(
        rda,
        rdb
    );
end

reg_file dut(
    reset,
    clk,
    ra,
    rb,
    wa,
    wda,
    reg_wr,
    rda,
    rdb
);

endmodule
