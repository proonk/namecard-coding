import io
from flask import Flask, render_template_string, request, send_file
from PIL import Image
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.pdfgen import canvas
import serverless_wsgi

app = Flask(__name__)


# 1. 绘制裁切角线核心逻辑
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

  line_dist_y = 1.0 * mm  # 竖向角线留白 0.1 cm
  line_dist_x = 5.0 * mm  # 左右横向角线留白 0.5 cm
  paper_margin = 3.0 * mm  # 纸张顶底留白 0.3 cm
  mark_len = 6.0 * mm  # 角线长度 0.6 cm

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

  # 顶底竖向角线
  for x_left in x_positions:
    x_right = x_left + card_w
    c.line(
        x_left, grid_top_y + line_dist_y, x_left, paper_h - paper_margin
    )
    c.line(
        x_right, grid_top_y + line_dist_y, x_right, paper_h - paper_margin
    )
    c.line(x_left, start_y - line_dist_y, x_left, paper_margin)
    c.line(x_right, start_y - line_dist_y, x_right, paper_margin)

  # 左右横向角线
  first_x = x_positions[0]
  last_x = x_positions[-1] + card_w
  for row in range(rows):
    y_bottom = start_y + row * (card_h + gutter_y)
    y_top = y_bottom + card_h
    c.line(
        first_x - line_dist_x,
        y_bottom,
        first_x - line_dist_x - mark_len,
        y_bottom,
    )
    c.line(
        first_x - line_dist_x, y_top, first_x - line_dist_x - mark_len, y_top
    )
    c.line(
        last_x + line_dist_x,
        y_bottom,
        last_x + line_dist_x + mark_len,
        y_bottom,
    )
    c.line(
        last_x + line_dist_x, y_top, last_x + line_dist_x + mark_len, y_top
    )

    if is_a3:
      center_x = paper_w / 2.0
      arm_len = 8.0 * mm
      c.line(center_x - arm_len, y_bottom, center_x + arm_len, y_bottom)
      c.line(center_x - arm_len, y_top, center_x + arm_len, y_top)

  # A3 中央分隔标记
  if is_a3:
    center_a3_line = paper_w / 2.0
    arm_len = 8.0 * mm
    c.line(
        center_a3_line, paper_margin, center_a3_line, paper_h - paper_margin
    )
    c.line(
        center_a3_line - arm_len, grid_top_y, center_a3_line + arm_len, grid_top_y
    )
    c.line(
        center_a3_line - arm_len, start_y, center_a3_line + arm_len, start_y
    )


# 2. 内存拼版生成器（直接接收 PIL Image 对象）
def generate_pdf_bytes(paper_choice, use_bleed, front_img, back_img):
  pdf_buffer = io.BytesIO()
  mm = 72 / 25.4

  card_w = 90.0 * mm
  card_h = 54.0 * mm
  gutter_x = 3.0 * mm
  gutter_y = 3.0 * mm
  bleed = 1.5 * mm if use_bleed else 0.0

  a4_block_w = 2 * card_w + gutter_x

  if str(paper_choice) == '1':
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
  else:
    paper_w, paper_h = portrait(A4)
    cols, rows = 2, 5
    is_a3 = False
    start_x_left = (paper_w - a4_block_w) / 2.0
    start_x_right = start_x_left
    x_positions = [start_x_left, start_x_left + card_w + gutter_x]

  grid_h = rows * card_h + (rows - 1) * gutter_y
  start_y = (paper_h - grid_h) / 2.0

  c = canvas.Canvas(pdf_buffer, pagesize=(paper_w, paper_h))

  # 页 1：正面
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
      c.drawInlineImage(
          front_img,
          x - bleed,
          y - bleed,
          width=card_w + 2 * bleed,
          height=card_h + 2 * bleed,
      )
  c.showPage()

  # 页 2：背面
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
      c.drawInlineImage(
          back_img,
          x - bleed,
          y - bleed,
          width=card_w + 2 * bleed,
          height=card_h + 2 * bleed,
      )
  c.showPage()

  c.save()
  pdf_buffer.seek(0)
  return pdf_buffer


# 3. 路由设置
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>名片自动拼版工具</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 40px auto; padding: 20px; border: 1px solid #ccc; borderRadius: 8px; }
        div { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="submit"] { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>名片自动化拼版工具</h2>
    <form action="/imposition" method="post" enctype="multipart/form-data">
        <div>
            <label>纸张规格：</label>
            <select name="paper_choice">
                <option value="1">A3 横向 (20张)</option>
                <option value="2">A4 竖向 (10张)</option>
            </select>
        </div>
        <div>
            <label>出血设置：</label>
            <input type="checkbox" name="use_bleed" value="true" checked> 添加 1.5mm 出血 (Bleed)
        </div>
        <div>
            <label>名片正面图片：</label>
            <input type="file" name="front" accept="image/*" required>
        </div>
        <div>
            <label>名片背面图片：</label>
            <input type="file" name="back" accept="image/*" required>
        </div>
        <div>
            <input type="submit" value="生成拼版 PDF">
        </div>
    </form>
</body>
</html>
"""


@app.route('/')
def index():
  return render_template_string(HTML_TEMPLATE)


@app.route('/imposition', methods=['POST'])
def process_imposition():
  paper_choice = request.form.get('paper_choice', '1')
  use_bleed = request.form.get('use_bleed') == 'true'

  front_file = request.files['front']
  back_file = request.files['back']

  # 直接读取为 Image 对象
  front_img = Image.open(front_file.stream)
  back_img = Image.open(back_file.stream)

  pdf_buffer = generate_pdf_bytes(
      paper_choice, use_bleed, front_img, back_img
  )

  return send_file(
      pdf_buffer,
      mimetype='application/pdf',
      as_attachment=True,
      download_name='Business_Cards_Imposition.pdf',
  )


# Netlify Serverless 导出的 handler
def handler(event, context):
  return serverless_wsgi.handle_request(app, event, context)


if __name__ == '__main__':
  app.run(debug=True, port=5000)