import os
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.pdfgen import canvas

def draw_marks_and_grid(c, paper_w, paper_h, card_w, card_h, cols, rows, start_x, start_y, gutter_x, gutter_y, is_a3):
    c.setLineWidth(0.4)
    mm = 72 / 25.4
    
    # 手量数据：角线留白与长度
    line_dist = 1.0 * mm    # 照片标注的 0.1 cm (1mm) 留白
    mark_len = 6.0 * mm     # 裁切角线长度 (6mm)

    # 1. 绘制列间的裁切角线（包含 0.3 cm 中缝双线）
    for col in range(cols):
        x_left = start_x + col * (card_w + gutter_x)
        x_right = x_left + card_w
        
        # 顶部竖向角线
        c.line(x_left, start_y + rows * card_h + (rows - 1) * gutter_y + line_dist, 
               x_left, start_y + rows * card_h + (rows - 1) * gutter_y + line_dist + mark_len)
        c.line(x_right, start_y + rows * card_h + (rows - 1) * gutter_y + line_dist, 
               x_right, start_y + rows * card_h + (rows - 1) * gutter_y + line_dist + mark_len)
        
        # 底部竖向角线
        c.line(x_left, start_y - line_dist, x_left, start_y - line_dist - mark_len)
        c.line(x_right, start_y - line_dist, x_right, start_y - line_dist - mark_len)

    # 2. 绘制行间的裁切角线
    for row in range(rows):
        y_bottom = start_y + row * (card_h + gutter_y)
        y_top = y_bottom + card_h
        
        grid_w = cols * card_w + (cols - 1) * gutter_x
        
        # 如果是 A3，正中间一行的贯穿长线避开重叠角线
        if not (is_a3 and row == 2):
            # 左侧横向角线
            c.line(start_x - line_dist, y_bottom, start_x - line_dist - mark_len, y_bottom)
            c.line(start_x - line_dist, y_top, start_x - line_dist - mark_len, y_top)
            
            # 右侧横向角线
            c.line(start_x + grid_w + line_dist, y_bottom, start_x + grid_w + line_dist + mark_len, y_bottom)
            c.line(start_x + grid_w + line_dist, y_top, start_x + grid_w + line_dist + mark_len, y_top)

    # 3. 只有 A3 横向才会绘制中央横贯长线 (Center Line)
    if is_a3:
        center_y = start_y + 2 * (card_h + gutter_y) + card_h / 2
        c.line(0, center_y, paper_w, center_y)

def make_imposition_pdf(paper_choice, front_path, back_path, output_pdf):
    mm = 72 / 25.4
    
    # 按照你手量的精准数据 (cm 转 mm)
    card_w = 90.0 * mm     # 9.0 cm
    card_h = 54.0 * mm     # 5.4 cm
    gutter_x = 3.0 * mm    # 0.3 cm 列中缝
    gutter_y = 3.0 * mm    # 0.3 cm 行缝隙
    margin_x = 14.0 * mm   # 1.4 cm 左右留白
    
    # 1 代表 A3 横向；2 代表 A4 竖向
    if paper_choice == '1':
        paper_w, paper_h = landscape(A3)
        cols, rows = 4, 5
        is_a3 = True
        paper_name = "A3 横向 (20张)"
    else:
        paper_w, paper_h = portrait(A4)
        cols, rows = 2, 5
        is_a3 = False
        paper_name = "A4 竖向 (10张)"

    # 计算整体版面位置 (使用你指定的 1.4 cm Margin 进行水平精准对齐)
    start_x = margin_x
    grid_h = rows * card_h + (rows - 1) * gutter_y
    start_y = (paper_h - grid_h) / 2  # 垂直方向自动居中

    output_dir = os.path.dirname(output_pdf)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    c = canvas.Canvas(output_pdf, pagesize=(paper_w, paper_h))
    
    # ----- 第 1 页：正面 -----
    draw_marks_and_grid(c, paper_w, paper_h, card_w, card_h, cols, rows, start_x, start_y, gutter_x, gutter_y, is_a3)
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (card_w + gutter_x)
            y = start_y + (rows - 1 - row) * (card_h + gutter_y)
            c.drawImage(front_path, x, y, width=card_w, height=card_h)
    c.showPage()
    
    # ----- 第 2 页：背面（自动左右镜像，保证短边翻转无缝重合） -----
    draw_marks_and_grid(c, paper_w, paper_h, card_w, card_h, cols, rows, start_x, start_y, gutter_x, gutter_y, is_a3)
    for row in range(rows):
        for col in range(cols):
            mirror_col = (cols - 1) - col
            x = start_x + mirror_col * (card_w + gutter_x)
            y = start_y + (rows - 1 - row) * (card_h + gutter_y)
            c.drawImage(back_path, x, y, width=card_w, height=card_h)
    c.showPage()
    
    c.save()
    print(f"\n拼版成功！已为你生成【{paper_name}】PDF 文件：{output_pdf}")

if __name__ == "__main__":
    print("====== 自动化名片拼版工具 ======")
    print("1. A3 横向 (20张)")
    print("2. A4 竖向 (10张 - 包含 0.3cm 中缝/缝隙与 1.4cm Margin)")
    choice = input("请选择纸张规格 (输入 1 或 2，按回车): ").strip()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    front_img = os.path.join(base_dir, 'img', 'front.png')
    back_img = os.path.join(base_dir, 'img', 'back.png')
    
    out_file = os.path.join(base_dir, 'Output_pdffile', 'Business_Cards_A3.pdf' if choice == '1' else 'Business_Cards_A4.pdf')
    make_imposition_pdf(choice, front_img, back_img, out_file)