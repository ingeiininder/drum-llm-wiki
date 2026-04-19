import easyocr
import os
from pathlib import Path

def run_local_ocr_easy(input_dir, output_dir):
    # 初始化辨識引擎
    print("正在啟動 EasyOCR 引擎 (語言: 英文)...")
    reader = easyocr.Reader(['en']) 
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 支援常見格式，改為遞迴搜尋所有子資料夾 (Recursive Search)
    extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp']
    images = []
    for ext in extensions:
        images.extend(list(input_path.rglob(ext)))
    
    if not images:
        print(f"在 {input_path.absolute()} 及其子資料夾中找不到任何圖片檔。")
        return

    print(f"找到 {len(images)} 張圖片，開始批次處理...")
    all_content = []

    for index, img_path in enumerate(images, 1):
        img_name = img_path.name
        print(f"[{index}/{len(images)}] 正在識別: {img_path.relative_to(input_path)}...")
        try:
            results = reader.readtext(str(img_path), detail=0)
            text = "\n".join(results)
            
            # 清理文字 (去除多餘空格)
            clean_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            
            # 儲存單獨檔案
            txt_name = f"{Path(img_name).stem}.txt"
            with open(output_path / txt_name, "w", encoding="utf-8") as f:
                f.write(clean_text)
            
            all_content.append(f"--- SOURCE: {img_name} ---\n{clean_text}\n" + "="*50)
        except Exception as e:
            print(f"處理 {img_name} 時發生異常: {e}")

    # 儲存總集篇
    summary_file = output_path / "all_extracted_text_easy.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_content))
    
    print(f"\n處理完成！成果存放在: {output_path.absolute()}")
    print(f"請將 {summary_file.name} 的內容提供給 AI 進行重製。")

if __name__ == "__main__":
    # 預設路徑設定: 指向專案內部的 data 目錄
    # 腳本位在 projects/groove-hub/pipeline/
    current_dir = Path(__file__).parent
    input_dir = current_dir.parent / "data" / "input"
    output_dir = current_dir.parent / "data" / "output"
    run_local_ocr_easy(input_dir, output_dir)
