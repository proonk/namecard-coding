import os
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.pdfgen import canvas


def draw_marks_and_grid(
    c,
    paper_w,
    paper_h,
    card_w,
    card_h,
    cols,
    rows,
    start_x_left,
    start_x_right,
    start_y,
    gutter_x,
    gutter_y,
    is_a3,
):
  c.setLineWidth(0.4)
  mm = 72 / 25.4

  line_dist = 1.0 * mm  # 角线距离卡片边缘留白 0.1 cm (1mm)
  paper_margin = 3.0 * mm  # 【核心修改】：距离 A3 纸张边缘留白 0.3 cm (3mm)

  if is_a3:
    x_positions = [
        start_x_left,
        start_x_left + card_w + gutter_x,
        start_x_right,
        start_x_right + card_w + gutter_x,
    ]
  else:
    x_positions = [start_x_left, start_x_left + card_w + gutter_x]

  grid_top_y = start_y + rows * card_h + (rows - 1) * gutter_y

  # 1. 绘制列间的裁切角线（顶部与底部竖向角线，顶端/底端统一距离纸张边缘留白 0.3cm）
  for x_left in x_positions:
    x_right = x_left + card_w

    # 顶部竖向角线：从 (卡片顶边 + 0.1cm) 向上画到 (纸张顶边 - 0.3cm)
    c.line(
        x_left, grid_top_y + line_dist, x_left, paper_h - paper_margin
    )
    c.line(
        x_right, grid_top_y + line_dist, x_right, paper_h - paper_margin
    )

    # 底部竖向角线：从 (卡片底边 - 0.1cm) 向下画到 (纸张底边 + 0.3cm)
    c.line(x_left, start_y - line_dist, x_left, paper_margin)
    c.line(x_right, start_y - line_dist, x_right, paper_margin)

  # 2. 绘制行间的裁切角线（左右两侧横向角线）
  mark_len = 6.0 * mm
  first_x = x_positions[0]
  last_x = x_positions[-1] + card_w

  for row in range(rows):
    y_bottom = start_y + row * (card_h + gutter_y)
    y_top = y_bottom + card_h

    # 最左侧横向角线
    c.line(
        first_x - line_dist,
        y_bottom,
        first_x - line_dist - mark_len,
        y_bottom,
    )
    c.line(first_x - line_dist, y_top, first_x - line_dist - mark_len, y_top)

    # 最右侧横向角线
    c.line(
        last_x + line_dist,
        y_bottom,
        last_x + line_dist + mark_len,
        y_bottom,
    )
    c.line(last_x + line_dist, y_top, last_x + line_dist + mark_len, y_top)

    # A3 中缝横向标记（直接贯穿穿过中央竖线，左右各 0.8cm）
    if is_a3:
      center_x = paper_w / 2.0
      arm_len = 8.0 * mm

      c.line(center_x - arm_len, y_bottom, center_x + arm_len, y_bottom)
      c.line(center_x - arm_len, y_top, center_x + arm_len, y_top)

  # 3. A3 中央分隔标记（中央竖向线上下两端同样距离纸张边缘留白 0.3cm）
  if is_a3:
    center_a3_line = paper_w / 2.0
    arm_len = 8.0 * mm  # 十字横向宽度 (0.8 cm)

    # 中央竖向线：从 (纸张底边 + 0.3cm) 画到 (纸张顶边 - 0.3cm)
    c.line(center_a3_line, paper_margin, center_a3_line, paper_h - paper_margin)

    # 网格最顶端与最底端的横向相交线
    c.line(
        center_a3_line - arm_len, grid_top_y, center_a3_line + arm_len, grid_top_y
    )
    c.line(
        center_a3_line - arm_len, start_y, center_a3_line + arm_len, start_y
    )


def make_imposition_pdf(paper_choice, front_path, back_path, output_pdf):
  mm = 72 / 25.4

  card_w = 90.0 * mm  # 9.0 cm
  card_h = 54.0 * mm  # 5.4 cm
  gutter_x = 3.0 * mm  # 0.3 cm 列中缝
  gutter_y = 3.0 * mm  # 0.3 cm 行缝隙

  a4_block_w = 2 * card_w + gutter_x

  if paper_choice == "1":
    paper_w, paper_h = landscape(A3)
    cols, rows = 4, 5
    is_a3 = True

    a4_w = paper_w / 2.0
    start_x_left = (a4_w - a4_block_w) / 2.0
    start_x_right = a4_w + start_x_left

    x_positions = [
        start_x_left,
        start_x_left + card_w + gutter_x,
        start_x_right,
        start_x_right + card_w + gutter_x,
    ]
    paper_name = "A3 横向 (纸张顶底边缘留白 0.3cm)"
  else:
    paper_w, paper_h = portrait(A4)
    cols, rows = 2, 5
    is_a3 = False

    start_x_left = (paper_w - a4_block_w) / 2.0
    start_x_right = start_x_left
    x_positions = [start_x_left, start_x_left + card_w + gutter_x]
    paper_name = "A4 竖向 (纸张顶底边缘留白 0.3cm)"

  grid_h = rows * card_h + (rows - 1) * gutter_y
  start_y = (paper_h - grid_h) / 2.0

  output_dir = os.path.dirname(output_pdf)
  if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir)

  c = canvas.Canvas(output_pdf, pagesize=(paper_w, paper_h))

  # ----- 第 1 页：正面 -----
  draw_marks_and_grid(
      c,
      paper_w,
      paper_h,
      card_w,
      card_h,
      cols,
      rows,
      start_x_left,
      start_x_right,
      start_y,
      gutter_x,
      gutter_y,
      is_a3,
  )
  for row in range(rows):
    for col in range(cols):
      x = x_positions[col]
      y = start_y + (rows - 1 - row) * (card_h + gutter_y)
      c.drawImage(front_path, x, y, width=card_w, height=card_h)
  c.showPage()

  # ----- 第 2 页：背面（短边翻转镜像对齐） -----
  draw_marks_and_grid(
      c,
      paper_w,
      paper_h,
      card_w,
      card_h,
      cols,
      rows,
      start_x_left,
      start_x_right,
      start_y,
      gutter_x,
      gutter_y,
      is_a3,
  )
  for row in range(rows):
    for col in range(cols):
      mirror_col = (cols - 1) - col
      x = x_positions[mirror_col]
      y = start_y + (rows - 1 - row) * (card_h + gutter_y)
      c.drawImage(back_path, x, y, width=card_w, height=card_h)
  c.showPage()

  c.save()
  print(
      f"\n拼版成功！已为你生成【{paper_name}】PDF"
      f" 文件：{output_pdf}"
  )


if __name__ == "__main__":
  print("====== 自动化名片拼版工具 ======")
  print("1. A3 横向 (20张)")
  print("2. A4 竖向 (10张)")
  choice = input("请选择纸张规格 (输入 1 或 2，按回车): ").strip()

  base_dir = os.path.dirname(os.path.abspath(__file__))
  front_img = os.path.join(base_dir, "img", "front.png")
  back_img = os.path.join(base_dir, "img", "back.png")

  out_file = os.path.join(
      base_dir,
      "Output_pdffile",
      "Business_Cards_A3.pdf"
      if choice == "1"
      else "Business_Cards_A4.pdf",
  )
  make_imposition_pdf(choice, front_img, back_img, out_file)