module tb_jmp_adder;

reg reset;
reg [31:0] read_addr;
reg [31:0] shl;
wire [31:0] jmp_addr;

initial begin
    $from_myhdl(
        reset,
        read_addr,
        shl
    );
    $to_myhdl(
        jmp_addr
    );
end

jmp_adder dut(
    reset,
    read_addr,
    shl,
    jmp_addr
);

endmodule
