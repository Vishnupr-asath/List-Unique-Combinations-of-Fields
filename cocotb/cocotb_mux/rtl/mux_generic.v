`timescale 1ns / 1ps

// A generic N-to-1 Multiplexer
module mux_generic #(
    parameter NUM_INPUTS = 8,
    parameter WIDTH      = 8,
    // Automatically calculate the width of the select line
    parameter SEL_WIDTH  = $clog2(NUM_INPUTS)
) (
    // --- FIX IS HERE: Changed from packed to unpacked array ---
    input  wire [WIDTH-1:0] data_in [NUM_INPUTS-1:0],
    input  wire [SEL_WIDTH-1:0]              sel,
    output wire [WIDTH-1:0]                  out
);

    // This assignment works for both packed and unpacked arrays in Verilog.
    // The select line directly indexes into the input array.
    assign out = data_in[sel];

endmodule
