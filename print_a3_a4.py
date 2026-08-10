import os
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.pdfgen import canvas

def draw_marks_and_grid(c, paper_w, paper_h, card_w, card_h, cols, rows, start_x_left, start_x_right, start_y, gutter_x, gutter_y, is_a3):
    c.setLineWidth(0.4)
    mm = 72 / 25.4
    
    line_dist = 1.0 * mm        # 0.1 cm (1mm) 角线留白
    mark_len = 6.0 * mm         # 0.6 cm (6mm) 裁切角线长度
    mark_len_custom = 4.0 * mm  # 0.4 cm (4mm) 角线延伸长度

    if is_a3:
        x_positions = [start_x_left, start_x_left + card_w + gutter_x, 
                       start_x_right, start_x_right + card_w + gutter_x]
    else:
        x_positions = [start_x_left, start_x_left + card_w + gutter_x]

    # 1. 绘制列间的裁切角线（顶端与底端的竖向角线）
    for x_left in x_positions:
        x_right = x_left + card_w
        
        # 顶部竖向角线
        c.line(x_left, start_y + rows * card_h + (rows - 1) * gutter_y + line_dist, 
               x_left, start_y + rows * card_h + (rows - 1) * gutter_y + line_dist + mark_len)
        c.line(x_right, start_y + rows * card_h + (rows - 1) * gutter_y + line_dist, 
               x_right, start_y + rows * card_h + (rows - 1) * gutter_y + line_dist + mark_len)
        
        # 底部竖向角线
        c.line(x_left, start_y - line_dist, x_left, start_y - line_dist - mark_len)
        c.line(x_right, start_y - line_dist, x_right, start_y - line_dist - mark_len)

    # 2. 绘制行间的裁切角线（横向角线）
    for row in range(rows):
        y_bottom = start_y + row * (card_h + gutter_y)
        y_top = y_bottom + card_h
        
        first_x = x_positions[0]
        last_x = x_positions[-1] + card_w
        
        # 最左侧横向角线
        c.line(first_x - line_dist, y_bottom, first_x - line_dist - mark_len, y_bottom)
        c.line(first_x - line_dist, y_top, first_x - line_dist - mark_len, y_top)
        
        # 最右侧横向角线
        c.line(last_x + line_dist, y_bottom, last_x + line_dist + mark_len, y_bottom)
        c.line(last_x + line_dist, y_top, last_x + line_dist + mark_len, y_top)
        
        # A3 中缝横向标记（保持 3ad92a0 版本原样：0.8cm 偏移 + 0.1cm 留白短线）
        if is_a3:
            center_x = paper_w / 2.0
            mid_offset = 8.0 * mm  # 0.8 cm
            
            x_mid_left = center_x - mid_offset
            x_mid_right = center_x + mid_offset
            
            c.line(x_mid_left + line_dist, y_bottom, x_mid_left + line_dist + mark_len, y_bottom)
            c.line(x_mid_left + line_dist, y_top, x_mid_left + line_dist + mark_len, y_top)
            
            c.line(x_mid_right - line_dist, y_bottom, x_mid_right - line_dist - mark_len, y_bottom)
            c.line(x_mid_right - line_dist, y_top, x_mid_right - line_dist - mark_len, y_top)

    # 3. A3 中央长线与最顶/最底相交横线（精准按照图片展示修改）
    if is_a3:
        center_a3_line = paper_w / 2.0  # 210mm (21cm)
        grid_h = rows * card_h + (rows - 1) * gutter_y
        
        top_y = start_y + grid_h
        bottom_y = start_y
        
        # 中央竖向长线：从最底角线延伸端穿到最顶角线延伸端
        c.line(center_a3_line, bottom_y - line_dist - mark_len_custom, 
               center_a3_line, top_y + line_dist + mark_len_custom)
        
        # 最顶端横向相交线（左右各 0.8 cm）
        arm_len = 8.0 * mm
        c.line(center_a3_line - arm_len, top_y, center_a3_line + arm_len, top_y)
        
        # 最底端横向相交线（左右各 0.8 cm，即你提供的图片样式）
        c.line(center_a3_line - arm_len, bottom_y, center_a3_line + arm_len, bottom_y)

def make_imposition_pdf(paper_choice, front_path, back_path, output_pdf):
    mm = 72 / 25.4
    
    card_w = 90.0 * mm     # 9.0 cm
    card_h = 54.0 * mm     # 5.4 cm
    gutter_x = 3.0 * mm    # 0.3 cm 列中缝
    gutter_y = 3.0 * mm    # 0.3 cm 行缝隙
    
    a4_block_w = 2 * card_w + gutter_x
    
    if paper_choice == '1':
        paper_w, paper_h = landscape(A3)
        cols, rows = 4, 5
        is_a3 = True
        
        a4_w = paper_w / 2.0  # 210mm
        start_x_left = (a4_w - a4_block_w) / 2.0
        start_x_right = a4_w + start_x_left
        
        x_positions = [
            start_x_left, 
            start_x_left + card_w + gutter_x,
            start_x_right, 
            start_x_right + card_w + gutter_x
        ]
        
        paper_name = "A3 横向 (精准顶底相交中线版)"
    else:
        paper_w, paper_h = portrait(A4)
        cols, rows = 2, 5
        is_a3 = False
        
        start_x_left = (paper_w - a4_block_w) / 2.0
        start_x_right = start_x_left
        x_positions = [start_x_left, start_x_left + card_w + gutter_x]
        
        paper_name = "A4 竖向 (10张 - 纯短角线)"

    grid_h = rows * card_h + (rows - 1) * gutter_y
    start_y = (paper_h - grid_h) / 2.0

    output_dir = os.path.dirname(output_pdf)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    c = canvas.Canvas(output_pdf, pagesize=(paper_w, paper_h))
    
    # ----- 第 1 页：正面 -----
    draw_marks_and_grid(c, paper_w, paper_h, card_w, card_h, cols, rows, start_x_left, start_x_right, start_y, gutter_x, gutter_y, is_a3)
    for row in range(rows):
        for col in range(cols):
            x = x_positions[col]
            y = start_y + (rows - 1 - row) * (card_h + gutter_y)
            c.drawImage(front_path, x, y, width=card_w, height=card_h)
    c.showPage()
    
    # ----- 第 2 页：背面（短边翻转镜像对齐） -----
    draw_marks_and_grid(c, paper_w, paper_h, card_w, card_h, cols, rows, start_x_left, start_x_right, start_y, gutter_x, gutter_y, is_a3)
    for row in range(rows):
        for col in range(cols):
            mirror_col = (cols - 1) - col
            x = x_positions[mirror_col]
            y = start_y + (rows - 1 - row) * (card_h + gutter_y)
            c.drawImage(back_path, x, y, width=card_w, height=card_h)
    c.showPage()
    
    c.save()
    print(f"\n拼版成功！已为你生成【{paper_name}】PDF 文件：{output_pdf}")

if __name__ == "__main__":
    print("====== 自动化名片拼版工具 ======")
    print("1. A3 横向 (20张 - 中央长线顶底相交版)")
    print("2. A4 竖向 (10张 - 纯短角线)")
    choice = input("请选择纸张规格 (输入 1 或 2，按回车): ").strip()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    front_img = os.path.join(base_dir, 'img', 'front.png')
    back_img = os.path.join(base_dir, 'img', 'back.png')
    
    out_file = os.path.join(base_dir, 'Output_pdffile', 'Business_Cards_A3.pdf' if choice == '1' else 'Business_Cards_A4.pdf')
    make_imposition_pdf(choice, front_img, back_img, out_file)