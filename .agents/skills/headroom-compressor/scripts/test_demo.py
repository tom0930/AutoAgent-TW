import json
from headroom import compress

def run_test():
    # 模擬 50 筆龐大的 FPGA / DMA Debug 日誌與 JSON 結構
    # 將整包 JSON 放在單一 system/tool 訊息，或是多筆 context 中
    json_logs = json.dumps([
        {
            "event_id": i,
            "status": "SUCCESS" if i != 27 else "FATAL_PARITY_ERROR",
            "timestamp": f"2026-08-02T21:50:{i:02d}Z",
            "module": "FPGA_DMA_Controller",
            "buffer_addr": hex(0x40000000 + i * 0x1000),
            "log_message": "Data transfer payload verification completed with zero errors" if i != 27 else "CRITICAL: Parity failure detected on memory bank 3 offset 0x040",
            "payload_bytes": [i * 2, i * 3, i * 4, i * 5],
            "retry_count": 0 if i != 27 else 3
        } for i in range(50)
    ], indent=2)

    raw_messages = [
        {"role": "system", "content": "You are a senior FPGA engineer analyzing DMA logs."},
        {"role": "user", "content": "Here are 50 DMA diagnostic log entries. Please check for errors:"},
        {"role": "tool", "content": json_logs}
    ]
    
    raw_str = json.dumps(raw_messages, ensure_ascii=False)
    orig_chars = len(raw_str)
    orig_tokens_est = orig_chars // 4
    
    print("=" * 65)
    print("🚀 Headroom 壓縮效果實測 (compress API with tool output)")
    print("=" * 65)
    print(f"原始輸入大小: {orig_chars} 字元 (預估 ~{orig_tokens_est} Tokens)\n")
    
    compressed_res = compress(raw_messages)
    
    compressed_messages = compressed_res.messages if hasattr(compressed_res, "messages") else compressed_res
    comp_str = json.dumps(compressed_messages, ensure_ascii=False) if isinstance(compressed_messages, (list, dict)) else str(compressed_messages)
    comp_chars = len(comp_str)
    comp_tokens_est = comp_chars // 4
    
    saving_ratio = (1 - (comp_chars / orig_chars)) * 100
    
    print(f"壓縮後大小:   {comp_chars} 字元 (預估 ~{comp_tokens_est} Tokens)")
    print(f"Token 節省率:  {saving_ratio:.2f}%")
    print(f"節省 Token 數: ~{orig_tokens_est - comp_tokens_est} Tokens")
    print("=" * 65)
    print("\n【Headroom SmartCrusher 壓縮後的傳送內容預覽】:\n")
    print(comp_str[:850] + "\n\n... [下略] ...")

if __name__ == "__main__":
    run_test()
