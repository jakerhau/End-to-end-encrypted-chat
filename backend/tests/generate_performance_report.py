"""
Performance Test Report Generator
Tạo biểu đồ và báo cáo từ kết quả performance tests
"""
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# Tạo thư mục output
OUTPUT_DIR = "performance_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==================== DỮ LIỆU PERFORMANCE TEST ====================
# (Cập nhật dựa trên kết quả chạy tests)

api_response_times = {
    "Login": 400,
    "Get Conversations": 5,
    "Get Friends": 5,
    "Get Pending Keys": 5,
    "Get Messages (50)": 50,
    "Register Public Key": 30,
    "Public Key Lookup": 6,
}

crypto_times = {
    "RSA Key Gen (10 keys)": 2130,
    "AES Encrypt (100 msgs)": 11,
    "AES Decrypt (100 msgs)": 41,
    "Session Key Exchange (50)": 1500,
    "PBKDF2 (100k iter)": 38,
    "Fingerprint (20)": 800,
}

concurrent_results = {
    "10 Concurrent Queries": 36,
    "10 Concurrent Key Regs": 200,
    "5 Concurrent Logins": 500,
}

throughput_data = {
    "API Throughput": 50,  # requests/second
    "Message Ops": 20,      # operations/second
}


def create_api_response_chart():
    """Biểu đồ API Response Time"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    labels = list(api_response_times.keys())
    values = list(api_response_times.values())
    colors = ['#2ecc71' if v < 100 else '#f1c40f' if v < 300 else '#e74c3c' for v in values]
    
    bars = ax.barh(labels, values, color=colors)
    ax.set_xlabel('Response Time (ms)', fontsize=12)
    ax.set_title('API Response Time Performance', fontsize=14, fontweight='bold')
    
    # Thêm giá trị trên mỗi bar
    for bar, value in zip(bars, values):
        ax.text(value + 5, bar.get_y() + bar.get_height()/2, 
                f'{value}ms', va='center', fontsize=10)
    
    # Thêm đường target
    ax.axvline(x=500, color='red', linestyle='--', label='Target: 500ms', alpha=0.7)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/api_response_time.png', dpi=150)
    plt.close()
    print(f"✅ Created: {OUTPUT_DIR}/api_response_time.png")


def create_crypto_performance_chart():
    """Biểu đồ Crypto Operations Performance"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    labels = list(crypto_times.keys())
    values = list(crypto_times.values())
    colors = ['#3498db', '#9b59b6', '#1abc9c', '#e67e22', '#34495e', '#e74c3c']
    
    bars = ax.barh(labels, values, color=colors)
    ax.set_xlabel('Time (ms)', fontsize=12)
    ax.set_title('Crypto Operations Performance', fontsize=14, fontweight='bold')
    
    for bar, value in zip(bars, values):
        ax.text(value + 20, bar.get_y() + bar.get_height()/2, 
                f'{value}ms', va='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/crypto_performance.png', dpi=150)
    plt.close()
    print(f"✅ Created: {OUTPUT_DIR}/crypto_performance.png")


def create_concurrent_requests_chart():
    """Biểu đồ Concurrent Requests Performance"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    labels = list(concurrent_results.keys())
    values = list(concurrent_results.values())
    
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=['#3498db', '#2ecc71', '#e74c3c'], width=0.5)
    
    ax.set_ylabel('Total Time (ms)', fontsize=12)
    ax.set_title('Concurrent Requests Performance', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15)
    
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'{value}ms', ha='center', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/concurrent_performance.png', dpi=150)
    plt.close()
    print(f"✅ Created: {OUTPUT_DIR}/concurrent_performance.png")


def create_throughput_chart():
    """Biểu đồ Throughput"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    labels = list(throughput_data.keys())
    values = list(throughput_data.values())
    
    colors = ['#3498db', '#2ecc71']
    bars = ax.bar(labels, values, color=colors, width=0.4)
    
    ax.set_ylabel('Operations per Second', fontsize=12)
    ax.set_title('System Throughput', fontsize=14, fontweight='bold')
    
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value} ops/s', ha='center', fontsize=12, fontweight='bold')
    
    ax.axhline(y=10, color='red', linestyle='--', label='Minimum: 10 ops/s', alpha=0.7)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/throughput.png', dpi=150)
    plt.close()
    print(f"✅ Created: {OUTPUT_DIR}/throughput.png")


def create_summary_dashboard():
    """Tạo dashboard tổng hợp"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Performance Test Dashboard', fontsize=16, fontweight='bold')
    
    # 1. API Response Time (Top Left)
    ax1 = axes[0, 0]
    labels = list(api_response_times.keys())
    values = list(api_response_times.values())
    colors = ['#2ecc71' if v < 100 else '#f1c40f' if v < 300 else '#e74c3c' for v in values]
    ax1.barh(labels, values, color=colors)
    ax1.set_xlabel('Time (ms)')
    ax1.set_title('API Response Time')
    
    # 2. Crypto Performance (Top Right)
    ax2 = axes[0, 1]
    labels = list(crypto_times.keys())[:4]  # Top 4
    values = list(crypto_times.values())[:4]
    ax2.barh(labels, values, color=['#3498db', '#9b59b6', '#1abc9c', '#e67e22'])
    ax2.set_xlabel('Time (ms)')
    ax2.set_title('Crypto Operations')
    
    # 3. Concurrent Performance (Bottom Left)
    ax3 = axes[1, 0]
    labels = list(concurrent_results.keys())
    values = list(concurrent_results.values())
    ax3.bar(labels, values, color=['#3498db', '#2ecc71', '#e74c3c'])
    ax3.set_ylabel('Time (ms)')
    ax3.set_title('Concurrent Requests')
    ax3.tick_params(axis='x', rotation=15)
    
    # 4. Throughput (Bottom Right)
    ax4 = axes[1, 1]
    labels = list(throughput_data.keys())
    values = list(throughput_data.values())
    ax4.bar(labels, values, color=['#3498db', '#2ecc71'])
    ax4.set_ylabel('Ops/Second')
    ax4.set_title('System Throughput')
    ax4.axhline(y=10, color='red', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/performance_dashboard.png', dpi=150)
    plt.close()
    print(f"✅ Created: {OUTPUT_DIR}/performance_dashboard.png")


def generate_all_reports():
    """Tạo tất cả báo cáo"""
    print("\n" + "="*50)
    print("📊 GENERATING PERFORMANCE REPORTS")
    print("="*50 + "\n")
    
    create_api_response_chart()
    create_crypto_performance_chart()
    create_concurrent_requests_chart()
    create_throughput_chart()
    create_summary_dashboard()
    
    print("\n" + "="*50)
    print(f"✅ All reports saved to: {OUTPUT_DIR}/")
    print("="*50)


if __name__ == "__main__":
    generate_all_reports()
