`define cntrl_w(a,b) tb_hydra_lux.odata[a*32+:32]=b;
`define cntrl_r(a,b) b=tb_hydra_lux.idata[a*32+:32];

module hydra_lux_cntrl #(parameter HYDRA_OFFS_O=0,parameter HYDRA_OFFS_I=0)
	();
// input

// conn_file: conn2.txt
// conn_file: conn0.txt

// tasks_to_generate
// io_frw_i/hydra/hydra2_0/inst/i_hydra_lux 
	bit [18:0] start_addr; // start_addr[]
	bit [18:0] frame_skip; // frame_skip[]
	bit [7:0]  nframes_cyc; // frames_cntr/maxval[] 
	bit nrst; // ../nrst
	bit stop_nframes; // stop_nframes
	bit [9:0] line_cntv; // line_cntr/val[]
	bit [7:0] frame_cntv; // frame_cntr/val[]
// }
// io_frw_i/hydra/hydra2_0/inst/bramin {
	bit [11:0] finaddr; // finaddr_reg[]/D
	bit stopf; //stopf_reg/D
	bit [11:0] addrb;  // addrb[]
	bit [2:0] ncyc;  // ncyc_reg[]/Q 
	bit ien;  // ien_reg 
// }	
// end_of_tasks_to_generate
/* autogenerated tasks */
	task cntrl_w0();
		bit [31:0] odata;
		odata[18:0]=frame_skip;
		odata[27:20]=nframes_cyc;
		odata[30]=stop_nframes;
		odata[31]=nrst;  		
		`cntrl_w(HYDRA_OFFS_O+0,odata);
	endtask
	task cntrl_w1();	
		bit [31:0] odata;
		odata[18:0]=start_addr;
		`cntrl_w(HYDRA_OFFS_O+1,odata);
	endtask
	task cntrl_w2();
		bit [31:0] odata;
		odata[11:0]=finaddr;
		odata[12]=stopf;
		`cntrl_w(HYDRA_OFFS_O+2,odata);
	endtask
	task cntrl_r0();
		bit [31:0] idata;
		`cntrl_r(HYDRA_OFFS_I+0,idata);
		addrb=idata[11:0];
		ncyc=idata[14:12];		
		ien=idata[15];
		frame_cntv=idata[23:16];
		line_cntv=idata[31:24];
	endtask
/* end autogenerated */

	task cntrl_w();
		cntrl_w2();
		cntrl_w1();
		cntrl_w0();
		#1;
		$write("[%t] cntrl_hydra_w\n  ",$time);
		i_hydra2.i_hydra_lux.ctrl_write();
		$display("");
		@(posedge tb_hydra_lux.clk);
	endtask	
endmodule

module SDIO_cntrl #(parameter OFFS_I=0, parameter OFFS_O=0);
// io_frw_i/IO2/lux_SDIO_0/inst {
	// reset bram, bramin, fifo, sub
	bit nrst; // nrst
	// wstrzymaj działanie SDIO
	bit pause; // pause	
// }
// io_frw_i/IO2/lux_SDIO_0/inst/bramin {
	bit [11:0] finaddr; // finaddr_reg[]/D
	bit stopf; //stopf_reg/D
	bit [11:0] addrb;  // addrb[]
	bit [2:0] ncyc;  // ncyc_reg[]/Q 
	bit ien;  // ien_reg 
// }		
endmodule

module RJ_cntrl #(parameter OFFS_I=0, parameter OFFS_O=0);
	// io_frw_i/IO2/RJ_front_0/inst {
	bit irq; // tm_i/irq
	bit irq_vec; // tm_i/irq_vec[]
	bit estate; // tm_i/jmp_condition/estate[]
	bit nrst_tm; // nrst
	bit ooser_rst;  // oser_rst_reg/D 
	bit PRSTN; // PRSTN_reg/D
	bit STDBYB; // STDBYB_reg/D
	bit RSTB; // RSTB_reg/D
	bit pc; // tm_i/pc[]
	//}
endmodule	

module lux_io_cntrl #(parameter OFFS_I=0, parameter OFFS_O=0);
	// io_frw_i/lux_in/lux_io_0/inst/sv {
	// nn_ld flagi ładowania: bitowo p[33],n[33],...p[1],n[1],p[0],n[0]
	// załadowanie podanej wartości dly_val lub bitslip następuje 
	// dla kanałów z ustawioną flagą
	bit bitslip_ld;// bitslip_ld[]
	bit dly_ld;// dly_ld_i/I0[] 
	/// reset delay+deser
	bit nrst; // nrst  
	bit dly_val; //desers[0].dei/dly_p_i/i/idel/CNTVALUEIN[] 
	// }
	// -o-flaga-	dly_ld_i/S

	task set_bitslip(input int ch, input [1:0] pn);
		bitslip[2*ch+:2]=pn;
	endtask
endmodule

module bitstat_cntrl #(parameter BS_OFFS_I=0, parameter BS_OFFS_O=0)
	();
//io_frw_i/lux_in/bitstat_0/inst {
	bit [11:0] xdata; //xdata0_i/I1[] 
	bit [11:0] xpclk; //xdata0_i__31/I1[]  
	
	bit rdy; // bbi/rdy_req/Q 
	bit [31:0] chr_concat [25]; /* ręcznie */	
//}	
	bit [6:0] diag; // io_frw_i/uP/AXI_CTRL_lux_0/inst/out2/slv_regs_reg[9][]/Q

	task cntrl_r(input int n);
		bit [31:0] idata;
		`cntrl_r(BS_OFFS_I+n,idata);
		chr_concat[n]=idata;
		if(n==24) begin
			rdy=idata[24];	
			diag=idata[31:25];		
		end
	endtask
/* autogenerated tasks */
	task cntrl_w0();	
		bit [31:0] odata;
		odata[11:0] =xdata;
		odata[23:12]=xpclk;
		`cntrl_w(BS_OFFS_O,odata);
	endtask
/* end autogenerated */
	function [1:0] chr(int bidx);
		int gn=bidx/6;
		int id=2*(bidx%6);
		chr=chr_concat[gn][id+:2];
	endfunction
	function int chsum(int ch);
		chsum=0;
		//int bidx[2]={24*ch,24*ch+23};
		// wytnij odpowiedni fragment
	endfunction
endmodule	

module deser_la_cntrl #(parameter OFFS_I=0, parameter OFFS_O=0);
	// io_frw_i/lux_in/deser_la_0/inst {
	bit nrst; // nrst
	bit clk_inv; // clk_inv
	bit [1:0] sel1s1; // ch_sel/sel1inst/s1_reg[]/D
	bit [1:0] sel1s2; // ch_sel/sel1inst/s2_reg[]/D
	bit [1:0] sel2s1; // ch_sel/sel2inst/s1_reg[]/D
	bit [1:0] sel2s2; // ch_sel/sel2inst/s2_reg[]/D
	bit [1:0] sel3s1; // ch_sel/sel3inst/s1_reg[]/D
	bit [1:0] sel3s2; // ch_sel/sel3inst/s2_reg[]/D
	//}
// io_frw_i/lux_in/deser_la_0/inst/bramin0 {
	bit [11:0] finaddr; // finaddr_reg[]/D
	bit stopf; //stopf_reg/D
	bit [11:0] addrb;  // addrb[]
	bit [2:0] ncyc;  // ncyc_reg[]/Q 
	bit ien;  // ien_reg 
// }		
// io_frw_i/lux_in/deser_la_0/inst/bramin1 {
	bit [11:0] finaddr1; // finaddr_reg[]/D
	bit stopf1; //stopf_reg/D
	bit [11:0] addrb1;  // addrb[]
	bit [2:0] ncyc1;  // ncyc_reg[]/Q 
	bit ien1;  // ien_reg 
// }		
endmodule	