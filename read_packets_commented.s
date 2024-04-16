handle_packet:
	addi	sp,sp,-32
	sw	ra,24(sp)
	sw	s0,16(sp)
	addi	s0,sp,32
.L2:
	lw	a5, 0(FIFO_READY)	# Load FIFO ready signal
	beq	a5,zero,.L2 		# While !ready
	
	lw	a5,0(FIFO_ADDR) 	# Read word from FIFO
	lw	a5,0(FIFO_ADDR)	
	andi a5,a5,65280		# clear all but the protocol bits
	addi a4,zero, 1536 		# Expected value for TCP
	bne	a4,a5,.L1			# if data != 1536: return
	
	lw a5,0(FIFO_ADDR)
	sw	a5,0(IP_BUFFER)

	lw a5,0(FIFO_ADDR)
	lw a5,0(FIFO_ADDR)
	andi a5,a5,524288 	# Check for psh flag
	addi a4,zero,524288
	bne	a4,a5,.L1

	lw a5,0(FIFO_ADDR)
	slli, a5,a5,32 			# Clear upper 32 bits of data
	srli, a5,a5,32

	sw	a5,0(FFT_ADDR) 		# Send data to FFT module

	j	.L6					# Jump to loop iterating through packet
.L7:
	lw a5,0(FIFO_ADDR)
	sw	a5,0(FFT_ADDR) 		# Send data to FFT module
.L6:
	lw	a5,0(FIFO_READY)
	bne	a5,zero,.L7
	j	.L1
.L1:
	ld	ra,24(sp)
	ld	s0,16(sp)
	addi	sp,sp,32
	jr	ra
main:
	addi	sp,sp,-16
	sd	ra,8(sp)
	sd	s0,0(sp)
	addi	s0,sp,16
.L11:
	call	handle_packet
	j	.L11
