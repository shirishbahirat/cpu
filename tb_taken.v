module tb_taken;

reg [31:0] result;
reg [0:0] brnch;
wire [0:0] pc_sel;

initial begin
    $from_myhdl(
        result,
        brnch
    );
    $to_myhdl(
        pc_sel
    );
end

taken dut(
    result,
    brnch,
    pc_sel
);

endmodule
