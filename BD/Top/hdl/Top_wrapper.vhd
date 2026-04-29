--Copyright 1986-2023 Xilinx, Inc. All Rights Reserved.
----------------------------------------------------------------------------------
--Tool Version: Vivado v.2022.2.2 (lin64) Build 3788238 Tue Feb 21 19:59:23 MST 2023
--Date        : Wed Apr 29 10:38:10 2026
--Host        : mlabNode191 running 64-bit Ubuntu 20.04.6 LTS
--Command     : generate_target Top_wrapper.bd
--Design      : Top_wrapper
--Purpose     : IP block netlist
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity Top_wrapper is
end Top_wrapper;

architecture STRUCTURE of Top_wrapper is
  component Top is
  end component Top;
begin
Top_i: component Top
 ;
end STRUCTURE;
