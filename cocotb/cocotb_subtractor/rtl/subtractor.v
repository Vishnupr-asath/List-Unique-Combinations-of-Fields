`timescale 1ns / 1ps

module subtractor #(
    parameter WIDTH = 4
) (
    input  wire [WIDTH-1:0] a,
    input  wire [WIDTH-1:0] b,
    output wire [WIDTH-1:0] diff,
    output wire               borrow_out
);


    wire [WIDTH:0] result;


    assign result = {1'b0, a} - {1'b0, b};


    assign diff = result[WIDTH-1:0];


    assign borrow_out = (a < b);


endmodule
