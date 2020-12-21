module tb_pc_assign;

reg reset;
wire [31:0] read_addr;
reg [31:0] pc;

initial begin
    $from_myhdl(
        reset,
        pc
    );
    $to_myhdl(
        read_addr
    );
end

pc_assign dut(
    reset,
    read_addr,
    pc
);

endmodule
