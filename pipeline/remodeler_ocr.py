import os
import pytesseract
from PIL import Image
from pathlib import Path

# 配置 Tesseract 路徑 (請根據你的安裝位置調整)
# 如果是 Windows，通常在 C:\Program Files\Tesseract-OCR\tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def remodel_ocr_extraction(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 建立輸出資料夾
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 取得圖片列表
    images = [f for f in os.listdir(input_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not images:
        print(f"在 {input_path.absolute()} 中找不到圖片。")
        return

    print(f"開始處理 {len(images)} 張圖片...")
    
    combined_text = []

    for img_name in images:
        img_full_path = input_path / img_name
        try:
            print(f"正在識別: {img_name}")
            img = Image.open(img_full_path)
            
            # 使用英文 OCR 識別
            text = pytesseract.image_to_string(img, lang='eng')
            
            # 清理多餘空行
            clean_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            
            # 儲存單獨檔案
            txt_name = f"{Path(img_name).stem}.txt"
            with open(output_path / txt_name, 'w', encoding='utf-8') as f:
                f.write(clean_text)
            
            combined_text.append(f"--- SOURCE: {img_name} ---\n{clean_text}\n")
            
        except Exception as e:
            print(f"處理 {img_name} 時發生錯誤: {e}")

    # 儲存總集篇，方便同步給 AI
    combined_file = output_path / "all_extracted_text.txt"
    with open(combined_file, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(combined_text))
    
    print(f"\n處理完成！請查看: {output_path.absolute()}")
    print(f"總集篇已生成: {combined_file.name}")

    # 預設路徑設定
    current_dir = Path(__file__).parent
    input_dir = current_dir.parent / "data" / "input"
    output_dir = current_dir.parent / "data" / "output"
    remodel_ocr_extraction(input_dir, output_dir)
