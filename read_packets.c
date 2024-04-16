int read_FIFO();
void send_to_FFT(int data);

void handle_packet(){
    int ready; // Special register
    int data; // Special register.

    int src_IP;
    while(!ready){;} // Loop until ready signal given
    
    data = read_FIFO(); // E.g. LW to a special address
    data = read_FIFO(); // Fetch second line of header
    data = data && 0b1111111100000000; // Clear all but the Protocol bits
    
    // Check protocol field is TCP
    if (data != 1536){ return; } // 6 << 8 = 1536

    data = read_FIFO(); // Fetch 3rd line of header
    src_IP = data; // Special SW instruction sends src_IP to  IP output buffer
    // Conditionally drop src_IP if Flag != 8
    
    data = read_FIFO(); // Fetch and ignore 4th line of header
    data = read_FIFO(); // Fetch 5th line of header
    data = data && 0b10000000000000000000; // Clear all bits except psh flag
    if(data != 524288){ return; } // 1 << 19 = 524288

    data = read_FIFO(); // Fetch 6th line of header
    data = data && 0b11111111111111111111111111111111; // Payload is contained in lower 4 bytes

    send_to_FFT(data);
    while(ready){ // FIFO should send a not ready signal when packet ends
        data = read_FIFO();
        send_to_FFT(data);
    }

    return;
}

int main(){
    while(1){ // Loop forever
        handle_packet(); // Poll for and handle incoming packets
    }
}