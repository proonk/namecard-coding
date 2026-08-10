from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.pdfgen import canvas

def draw_marks_and_grid(c, paper_w, paper_h, card_w, card_h, cols, rows, start_x, start_y, is_a3):
    c.setLineWidth(0.4)
    mm = 72 / 25.4
    line_dist = 3.0 * mm    # 留白 3mm
    mark_len = 6.0 * mm     # 角线长 6mm
    grid_w = cols * card_w
    grid_h = rows * card_h

    # 1. 四周与列间竖向裁切角线
    for col in range(cols + 1):
        x = start_x + col * card_w
        c.line(x, start_y + grid_h + line_dist, x, start_y + grid_h + line_dist + mark_len)
        c.line(x, start_y - line_dist, x, start_y - line_dist - mark_len)
        
    # 2. 行间横向裁切角线
    for row in range(rows + 1):
        y = start_y + row * card_h
        
        # 如果是 A3，避开中间贯穿长线的位置，避免跟角线重叠
        if is_a3 and row == 2:
            continue
            
        c.line(start_x - line_dist, y, start_x - line_dist - mark_len, y)
        c.line(start_x + grid_w + line_dist, y, start_x + grid_w + line_dist + mark_len, y)
        
        # 中缝短线 (Gutters Marks)
        for col in range(1, cols):
            mid_x = start_x + col * card_w
            c.line(mid_x - mark_len / 2, y, mid_x + mark_len / 2, y)

    # 3. 只有 A3 横向才会绘制中央贯穿长线 (Center Line)，A4 竖向完全不画
    if is_a3:
        center_y = start_y + 2.5 * card_h
        c.line(0, center_y, paper_w, center_y)

def make_imposition_pdf(paper_choice, front_path, back_path, output_pdf):
    mm = 72 / 25.4
    card_w = 90 * mm
    card_h = 54 * mm
    
    # 1 代表 A3 横向；其它代表 A4 竖向
    if paper_choice == '1':
        paper_w, paper_h = landscape(A3)
        cols, rows = 4, 5
        is_a3 = True
        paper_name = "A3 横向 (带贯穿长线)"
    else:
        paper_w, paper_h = portrait(A4)
        cols, rows = 2, 5
        is_a3 = False
        paper_name = "A4 竖向 (纯短角线)"

    grid_w = cols * card_w
    grid_h = rows * card_h
    start_x = (paper_w - grid_w) / 2
    start_y = (paper_h - grid_h) / 2

    c = canvas.Canvas(output_pdf, pagesize=(paper_w, paper_h))
    
    # 第 1 页：正面
    draw_marks_and_grid(c, paper_w, paper_h, card_w, card_h, cols, rows, start_x, start_y, is_a3)
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * card_w
            y = start_y + (rows - 1 - row) * card_h
            c.drawImage(front_path, x, y, width=card_w, height=card_h)
    c.showPage()
    
    # 第 2 页：背面（短边翻转自动左右镜像对齐）
    draw_marks_and_grid(c, paper_w, paper_h, card_w, card_h, cols, rows, start_x, start_y, is_a3)
    for row in range(rows):
        for col in range(cols):
            mirror_col = (cols - 1) - col
            x = start_x + mirror_col * card_w
            y = start_y + (rows - 1 - row) * card_h
            c.drawImage(back_path, x, y, width=card_w, height=card_h)
    c.showPage()
    
    c.save()
    print(f"\n拼版成功！已为你生成【{paper_name}】PDF 文件：{output_pdf}")

if __name__ == "__main__":
    print("====== 自动化名片拼版工具 ======")
    print("1. A3 横向 (Landscape - 20张 - 带中央长贯穿线)")
    print("2. A4 竖向 (Portrait - 10张 - 纯标准短角线)")
    choice = input("请选择纸张规格 (输入 1 或 2，按回车): ").strip()
    
    front_img = '1000085015.jpg'
    back_img = '1000085016.jpg'
    
    out_file = 'Business_Cards_A3.pdf' if choice == '1' else 'Business_Cards_A4.pdf'
    make_imposition_pdf(choice, front_img, back_img, out_file)