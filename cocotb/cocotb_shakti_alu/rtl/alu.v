`timescale 1ns / 1ps

module alu (
    input  wire [31:0] operand_a,
    input  wire [31:0] operand_b,
    input  wire [3:0]  alu_opcode,
    output reg  [31:0] result,
    output wire        zero_flag
);

    // Operation codes for common RV32I instructions
    localparam ALU_ADD  = 4'b0000;
    localparam ALU_SUB  = 4'b0001;
    localparam ALU_SLL  = 4'b0010; // Shift Left Logical
    localparam ALU_SLT  = 4'b0011; // Set Less Than (Signed)
    localparam ALU_SLTU = 4'b0100; // Set Less Than (Unsigned)
    localparam ALU_XOR  = 4'b0101;
    localparam ALU_SRL  = 4'b0110; // Shift Right Logical
    localparam ALU_SRA  = 4'b0111; // Shift Right Arithmetic
    localparam ALU_OR   = 4'b1000;
    localparam ALU_AND  = 4'b1001;

    // Combinational logic for ALU operations
    always_comb begin
        case (alu_opcode)
            ALU_ADD:  result = operand_a + operand_b;
            ALU_SUB:  result = operand_a - operand_b;
            ALU_SLL:  result = operand_a << operand_b[4:0]; // Shift amount is lower 5 bits of operand_b
            ALU_SLT:  result = ($signed(operand_a) < $signed(operand_b)) ? 32'd1 : 32'd0;
            ALU_SLTU: result = (operand_a < operand_b) ? 32'd1 : 32'd0;
            ALU_XOR:  result = operand_a ^ operand_b;
            ALU_SRL:  result = operand_a >> operand_b[4:0];
            ALU_SRA:  result = $signed(operand_a) >>> operand_b[4:0];
            ALU_OR:   result = operand_a | operand_b;
            ALU_AND:  result = operand_a & operand_b;
            default:  result = 32'hdeadbeef; // Default case for undefined opcodes
        endcase
    end

    // The zero flag is asserted if the result is zero.
    // This is used for branch instructions like BEQ and BNE.
    assign zero_flag = (result == 32'b0);

endmodule
