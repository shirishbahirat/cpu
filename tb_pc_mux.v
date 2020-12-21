module tb_pc_mux;

reg reset;
wire [31:0] pc;
reg [31:0] pc_addr;
reg [31:0] jmp_addr;
reg [0:0] pc_sel;

initial begin
    $from_myhdl(
        reset,
        pc_addr,
        jmp_addr,
        pc_sel
    );
    $to_myhdl(
        pc
    );
end

pc_mux dut(
    reset,
    pc,
    pc_addr,
    jmp_addr,
    pc_sel
);

endmodule
