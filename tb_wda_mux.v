module tb_wda_mux;

reg reset;
wire [31:0] wda;
reg [0:0] mem_to_rgs;
reg [31:0] result;
reg [31:0] read_data;

initial begin
    $from_myhdl(
        reset,
        mem_to_rgs,
        result,
        read_data
    );
    $to_myhdl(
        wda
    );
end

wda_mux dut(
    reset,
    wda,
    mem_to_rgs,
    result,
    read_data
);

endmodule
