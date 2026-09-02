//------------------------------------------------------------------------------ 
// Copyright (c) 2004 Xilinx, Inc. 
// All Rights Reserved 
//------------------------------------------------------------------------------ 
//   ____  ____ 
//  /   /\/   / 
// /___/  \  /   Vendor: Xilinx 
// \   \   \/    Author: Reed Tidwell, Advanced Product Division, Xilinx, Inc.
//  \   \        Filename: $RCSfile: alpha_blend_top.v,v $
//  /   /        Date Last Modified:  $Date: 2004-12-14 10:05:12-07 $
// /___/   /\    Date Created: October 18, 2004 
// \   \  /  \ 
//  \___\/\___\ 
// 
//
// Revision History: 
// $Log: alpha_blend_top.v,v $
// Revision 1.5  2004-12-14 10:05:12-07  reedt
// Corrected pixclk_out to clk1x for compiling with wrapper.
//
// Revision 1.4  2004-12-06 10:11:13-07  reedt
// Added Rounding for App note 706
//
// Revision 1.3  2004-11-18 09:52:59-07  reedt
// Changed clock follower, fol_clk1x, to be 2 FF stages instead of 3.
//
// Revision 1.2  2004-11-09 16:40:51-07  reedt
// Removed align register.  Added 2nd internal delay in DSP.  Added clock follower.  Debugged VHDL and Verilog versions.
//
// Revision 1.1  2004-10-26 13:56:49-06  reedt
// Completed blend simulation with picture files.
//
// Revision 1.0  2004-10-19 10:55:08-06  reedt
// Video stream blender with inputs for 2 sets of RGB & DE plus
// an Alpha stream and alpha DE.  Simulation compile OK.
//
// Revision 1.0  2004-10-19 10:16:14-06  reedt
// Video stream blender with inputs for 2 sets of RGB & DE plus
// an Alpha stream and alpha DE.  Initial checkin is before compile.
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

module alpha_blend_top (
  input            pixclk,
  input            reset,
  input            hsync_strm0,
  input            vsync_strm0,
  input            de_strm0,
  input      [9:0] r_strm0,
  input      [9:0] g_strm0,
  input      [9:0] b_strm0, 
  input            de_strm1,
  input      [9:0] r_strm1,
  input      [9:0] g_strm1,
  input      [9:0] b_strm1,
  input            de_alpha, 
  input      [9:0] alpha_strm,
  
  output            pixclk_out,
  output            hsync_blnd,
  output            vsync_blnd,
  output            de_blnd,
  output     [9:0]  r_blnd,
  output     [9:0]  g_blnd,
  output     [9:0]  b_blnd,
  output            dcm_locked 
);
  wire              clk1x;      // 1x clock from DCM
  wire              clk2x;      // 2x clock from DCM
  reg               fol_clk1x;  // clock follower of clk1x in clk2x domain
  reg               toggle;
  reg               toggle_1;
// for multiplicands, repeat MSBs in the LSBs for greater range  
  wire      [17:0]  video0_r =  {1'b0, r_strm0, r_strm0[9:3]};  
  wire      [17:0]  video0_g =  {1'b0, g_strm0, g_strm0[9:3]};
  wire      [17:0]  video0_b =  {1'b0, b_strm0, b_strm0[9:3]};
  wire      [17:0]  video1_r =  {1'b0, r_strm1, r_strm1[9:3]};  
  wire      [17:0]  video1_g =  {1'b0, g_strm1, g_strm1[9:3]};
  wire      [17:0]  video1_b =  {1'b0, b_strm1, b_strm1[9:3]};
  wire      [17:0]  alpha;
  wire      [17:0]  one_minus_alpha;
  wire      [47:0]  blend_r;        // outputs from DSP48
  wire      [47:0]  blend_g;
  wire      [47:0]  blend_b;
  wire      [47:0]  round;          // rounding constant
  reg               hsync_1, hsync_2, hsync_3, hsync_4;
  reg               vsync_1, vsync_2, vsync_3, vsync_4;
  reg               de_1, de_2, de_3, de_4;

  assign    alpha = de_alpha?  {1'b0,alpha_strm, alpha_strm[9:3]}: 18'h1FFFF;
  assign    one_minus_alpha = de_alpha?{1'b0,~alpha_strm,~alpha_strm[9:3]}: 0;
  assign    round =  48'h000000010000;
  assign    pixclk_out = clk1x;
//
// select output bits from 48 bit accumulator
//
  assign    r_blnd = blend_r[33:24];
  assign    g_blnd = blend_g[33:24];
  assign    b_blnd = blend_b[33:24];
  assign    hsync_blnd = hsync_4;
  assign    vsync_blnd = vsync_4;
  assign    de_blnd = de_4;
  // 
  // delay syncs to match rgb data
  //
  always @ (posedge clk1x) begin
    hsync_1 <= hsync_strm0;
    hsync_2 <= hsync_1;
    hsync_3 <= hsync_2;
    hsync_4 <= hsync_3;
    vsync_1 <= vsync_strm0;
    vsync_2 <= vsync_1;
    vsync_3 <= vsync_2;
    vsync_4 <= vsync_3;
    de_1 <= de_strm0;
    de_2 <= de_1;
    de_3 <= de_2;   
    de_4 <= de_3;   
  end  // always
  // create clock following circuit
  always @ (posedge clk1x or posedge reset) begin
    if (reset)
      toggle <= 0;
    else
      toggle <= !toggle;
  end
  always @ (posedge clk2x) begin
    toggle_1 <= toggle;
    fol_clk1x <= ! (toggle ^ toggle_1);
  end
  
  //
  // Create 1x and 2x clccks
  //
DCM_1x_2x dcm_1x_2x (
    .CLKIN_IN(pixclk), 
    .RST_IN(reset), 
    .CLKIN_IBUFG_OUT(), 
    .CLK0_OUT(clk1x), 
    .CLK2X_OUT(clk2x), 
    .LOCKED_OUT(dcm_locked)
    );
 //
 // instantiate blend units for R G and B
 //    
 dual_stream_blend   red_blender(
   .clk1x    (clk1x),  
   .clk2x    (clk2x),  
   .reset    (reset),
   .fol_clk1x(fol_clk1x),
   .video0   (video0_r),         
   .video1   (video1_r),        
   .alpha    (alpha),          
   .one_minus_alpha  (one_minus_alpha),
   .round    (round),
    
   .blend    (blend_r)        
);
 dual_stream_blend   green_blender(
   .clk1x    (clk1x),  
   .clk2x    (clk2x),  
   .reset    (reset),
   .fol_clk1x(fol_clk1x),
   .video0   (video0_g),         
   .video1   (video1_g),        
   .alpha    (alpha),          
   .one_minus_alpha  (one_minus_alpha),
   .round    (round),
    
   .blend    (blend_g)        
);
 dual_stream_blend   blue_blender(
   .clk1x    (clk1x),  
   .clk2x    (clk2x),  
   .reset    (reset),
   .fol_clk1x(fol_clk1x),
   .video0   (video0_b),         
   .video1   (video1_b),        
   .alpha    (alpha),          
   .one_minus_alpha  (one_minus_alpha),
   .round    (round),
    
   .blend    (blend_b)        
);

endmodule	
