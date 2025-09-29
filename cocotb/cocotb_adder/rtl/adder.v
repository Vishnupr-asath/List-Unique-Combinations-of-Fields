`timescale 1ns / 1ps

module adder (
    input  wire [3:0] a,
    input  wire [3:0] b,
    output wire [3:0] sum
);

    // This is a simple combinational adder
    assign sum = a + b;

endmodule
