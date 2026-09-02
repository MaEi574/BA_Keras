//------------------------------------------------------------------------------ 
// Copyright (c) 2004 Xilinx, Inc. 
// All Rights Reserved 
//------------------------------------------------------------------------------ 
//   ____  ____ 
//  /   /\/   / 
// /___/  \  /   Vendor: Xilinx 
// \   \   \/    Author: Reed Tidwell, Advanced Product Division, Xilinx, Inc.
//  \   \        Filename: $RCSfile: dual_stream_blend.v,v $
//  /   /        Date Last Modified:  $Date: 2004-12-06 10:11:13-07 $
// /___/   /\    Date Created: August 18, 2004 
// \   \  /  \ 
//  \___\/\___\ 
// 
//
// Revision History: 
// $Log: dual_stream_blend.v,v $
// Revision 1.3  2004-12-06 10:11:13-07  reedt
// Added Rounding for App note 706
//
// Revision 1.2  2004-11-09 16:40:51-07  reedt
// Removed align register.  Added 2nd internal delay in DSP.  Added clock follower.  Debugged VHDL and Verilog versions.
//
// Revision 1.1  2004-10-26 13:56:49-06  reedt
// Completed blend simulation with picture files.
//
// Revision 1.0  2004-09-20 17:22:32-06  reedt
// Initial Checkin
//
//------------------------------------------------------------------------------ 
//
//     XILINX IS PROVIDING THIS DESIGN, CODE, OR INFORMATION "AS IS"
//     SOLELY FOR USE IN DEVELOPING PROGRAMS AND SOLUTIONS FOR
//     XILINX DEVICES.  BY PROVIDING THIS DESIGN, CODE, OR INFORMATION
//     AS ONE POSSIBLE IMPLEMENTATION OF THIS FEATURE, APPLICATION
//     OR STANDARD, XILINX IS MAKING NO REPRESENTATION THAT THIS
//     IMPLEMENTATION IS FREE FROM ANY CLAIMS OF INFRINGEMENT,
//     AND YOU ARE RESPONSIBLE FOR OBTAINING ANY RIGHTS YOU MAY REQUIRE
//     FOR YOUR IMPLEMENTATION.  XILINX EXPRESSLY DISCLAIMS ANY
//     WARRANTY WHATSOEVER WITH RESPECT TO THE ADEQUACY OF THE
//     IMPLEMENTATION, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OR
//     REPRESENTATIONS THAT THIS IMPLEMENTATION IS FREE FROM CLAIMS OF
//     INFRINGEMENT, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
//     FOR A PARTICULAR PURPOSE.
//
//------------------------------------------------------------------------------
`timescale 1ns / 10ps
module  dual_stream_blend  (
  input                 clk1x,    // Input and output rate clock
  input                 clk2x,    // Frequency doubled clock for DSP operation
  input                 reset,
  input                 fol_clk1x, // clock follower of clk1x
  input     [17:0]      video0,         // Data Stream 0 A value
  input     [17:0]      video1,         // Data Stream 1 A value
  input     [17:0]      alpha,          // Data Stream 0 B value
  input     [17:0]      one_minus_alpha,// Data Stream 1 B value
  input     [47:0]      round,          // Rounding constant
  
  output reg   [47:0]      blend          // Blended output data stream
);

  reg       [17:0]      vid0_in;        // Registers for moudule inputs
  reg       [17:0]      vid1_in;
  reg       [17:0]      alpha_in;
  reg       [17:0]      one_minus_in;
  reg                   mux_sel;       // Mux select for DDR mux
  reg                   blend_pass;     // Mux select for DSP 48 Z mux
  wire      [17:0]      dspA;           // DSP48 A input 
  wire      [17:0]      dspB;           // DSP48 B input
  wire      [47:0]      dspP;           // DSP48 output
  wire      [6:0]       opmode;         // OPMODE input to DSP48
  
  // define input muxes
  assign        dspA = mux_sel? vid1_in: vid0_in;
  assign        dspB = mux_sel? one_minus_in: alpha_in;
  assign        opmode =   {1'b0, 1'b1, !blend_pass,4'h5 };
  
  // define clk1x registers
  always @(posedge clk1x or posedge reset) begin
    if (reset) begin
      vid0_in <= 0;
      vid1_in <= 0;
      alpha_in <= 0;
      one_minus_in <= 0;
      blend <= 0;  
    end
    else  begin// not reset
      vid0_in <= video0 ;
      vid1_in <= video1;
      alpha_in <= alpha;
      one_minus_in <= one_minus_alpha;
      blend <= dspP;
    end   // not reset
  end  // always
  
  //  implement synchronous control signals
  always @(posedge clk2x or posedge reset) begin
    if (reset) begin
      mux_sel <= 0;
      blend_pass <= 0;
    end
    else begin // not reset
      mux_sel <= fol_clk1x;
      blend_pass <= fol_clk1x;
    end  // not reset
  end    // always
  // instance DSP 48 
  DSP48 alpha_blend
  (
    .A(dspA),             // Input A to Multiplier
    .B(dspB),             // Input B to Multiplier
    .C(round), // Input C to Adder,  Round to 17 bits
    .BCIN(18'b0),          //
    .PCIN(48'b0),          //
    .OPMODE(opmode),   //
    .SUBTRACT(1'b0),       //
    .CARRYIN(1'b0),        //
    .CARRYINSEL(2'b00),    //
    .CLK(clk2x),             //
    .CEA(1'b1),            //
    .CEB(1'b1),            //
    .CEC(1'b1),            //
    .CEP(1'b1),            //
    .CEM(1'b1),            //
    .CECTRL(1'b1),         //
    .CECARRYIN(1'b1),      //
	.CECINSUB(1'b1),       //
    .RSTA(reset),            //
    .RSTB(reset),            //
    .RSTC(reset),            //
    .RSTP(reset),            //
    .RSTM(reset),            //
    .RSTCTRL(reset),         //
    .RSTCARRYIN(reset),      //
    .BCOUT(),       //
    .P(dspP),                  //
    .PCOUT()        //
  );

//synthesis attribute AREG of alpha_blend is "2";
//synthesis attribute BREG of alpha_blend is "2";
//synthesis attribute CREG of alpha_blend is "0";
//synthesis attribute CARRYINREG of alpha_blend is "0";
//synthesis attribute MREG of alpha_blend is "1";
//synthesis attribute PREG of alpha_blend is "1";
//synthesis attribute OPMODEREG of alpha_blend is "1";
//synthesis attribute SUBTRACTREG of alpha_blend is "0";
//synthesis attribute CARRYINSELREG of alpha_blend is "0";
//synthesis attribute B_INPUT of alpha_blend is "DIRECT";
 //synthesis attribute LEGACY_MODE of alpha_blend is ""MULT18X18S";

//synthesis translate_off 
defparam alpha_blend.AREG = 2'b10;
defparam alpha_blend.BREG = 2'b10;
defparam alpha_blend.CREG = 2'b00;
defparam alpha_blend.CARRYINREG = 1'b0;
defparam alpha_blend.MREG = 1'b1;
defparam alpha_blend.PREG = 1'b1;
defparam alpha_blend.OPMODEREG = 1'b1;
defparam alpha_blend.SUBTRACTREG = 1'b0;
defparam alpha_blend.CARRYINSELREG = 1'b0;
defparam alpha_blend.B_INPUT = "DIRECT";
defparam alpha_blend.LEGACY_MODE = "MULT18X18S";
//synthesis translate_on

 
      


endmodule	
