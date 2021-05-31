module tb_idex_pipl;

reg reset;
wire [152:0] idex_reg;
reg [31:0] instruction;
reg [4:0] ra;
reg [4:0] rb;
reg [4:0] wa;
reg [31:0] im_gen;
reg [31:0] rda;
reg [31:0] rdb;
reg [3:0] alu_op;
reg [0:0] brnch;
reg [0:0] mem_rd;
reg [0:0] mem_to_rgs;
reg [0:0] mem_wr;
reg [0:0] alu_src;
reg [0:0] reg_wr;

initial begin
    $from_myhdl(
        reset,
        instruction,
        ra,
        rb,
        wa,
        im_gen,
        rda,
        rdb,
        alu_op,
        brnch,
        mem_rd,
        mem_to_rgs,
        mem_wr,
        alu_src,
        reg_wr
    );
    $to_myhdl(
        idex_reg
    );
end

idex_pipl dut(
    reset,
    idex_reg,
    instruction,
    ra,
    rb,
    wa,
    im_gen,
    rda,
    rdb,
    alu_op,
    brnch,
    mem_rd,
    mem_to_rgs,
    mem_wr,
    alu_src,
    reg_wr
);

endmodule
