import easyocr
import os
import time
import argparse
from pathlib import Path

def process_single_image(reader, img_path, output_path):
    """處理單張圖片的辨識與儲存"""
    img_name = img_path.name
    try:
        # paragraph=True 提升結構品質, detail=0 提升速度
        results = reader.readtext(str(img_path), paragraph=True, detail=0)
        text = "\n".join(results)
        
        # 清理文字
        clean_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
        
        # 儲存單獨檔案
        txt_name = f"{img_path.stem}.txt"
        with open(output_path / txt_name, "w", encoding="utf-8") as f:
            f.write(clean_text)
            
        return f"--- SOURCE: {img_name} ---\n{clean_text}\n" + "="*50
    except Exception as e:
        return f"Error processing {img_name}: {e}"

def run_parallel_ocr(input_dir, output_dir, max_workers=4):
    print(f"啟動優化版 OCR 引擎...")
    print(f"正在檢查硬體加速...")
    
    import torch
    use_gpu = torch.cuda.is_available()
    print(f"CUDA 可用性: {use_gpu}")
    
    # 初始化辨識引擎
    reader = easyocr.Reader(['en'], gpu=use_gpu) 
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp']
    images = []
    for ext in extensions:
        images.extend(list(input_path.rglob(ext)))
    
    if not images:
        print(f"找不到圖片檔案於: {input_path}")
        return

    print(f"找到 {len(images)} 張圖片。")
    print(f"模式啟動 (序列化單工, 結構品質優先, GPU加速)")
    
    all_content = []
    start_time = time.time()

    for i, img in enumerate(images, 1):
        result = process_single_image(reader, img, output_path)
        all_content.append(result)
        if i % 10 == 0 or i == len(images):
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = avg_time * (len(images) - i)
            print(f"進度: [{i}/{len(images)}] | 平均: {avg_time:.2f}s/頁 | 預計剩餘: {remaining/60:.1f}分")

    # 儲存總集篇
    summary_file = output_path / "all_extracted_text_optimized.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_content))
    
    total_time = time.time() - start_time
    print(f"\n任務完成！")
    print(f"總耗時: {total_time/60:.2f} 分鐘")
    print(f"成果存放在: {output_path.absolute()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GPU 加速並行 OCR 工具")
    parser.add_argument("--input", type=str, help="輸入圖片資料夾路徑")
    parser.add_argument("--output", type=str, help="輸出文字資料夾路徑")
    parser.add_argument("--workers", type=int, default=4, help="並行執行緒數")
    
    args = parser.parse_args()
    
    current_dir = Path(__file__).parent
    
    # 若未指定則使用預設路徑
    input_folder = Path(args.input) if args.input else current_dir.parent / "data" / "input"
    output_folder = Path(args.output) if args.output else current_dir.parent / "data" / "output"
    
    run_parallel_ocr(input_folder, output_folder, max_workers=args.workers)
