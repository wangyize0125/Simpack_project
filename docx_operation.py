# -*-coding:utf-8 -*-
# @Time    : 2021/7/5 4:12 下午
# @Author  : Yize Wang
# @File    : docx_operation.py
# @Software: PyCharm

from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.dml import MSO_THEME_COLOR_INDEX

import app_constants


class DocxFile:
    """
    create docx file
    """

    # maximum size of the figures
    fig_x_max = 14
    fig_cap_size = 10
    table_size = 10
    heading_sizes = [14, 14, 12]

    def __init__(self, filename):
        self.filename = filename + ".docx"

        self.doc = Document(app_constants.word_template)
        self.styles = self.doc.styles

        self.num_fig = 0
        self.num_heading = [0 for i in range(len(self.heading_sizes))]

        # add styles
        self.fig_caption = self.styles.add_style("fig_caption", WD_STYLE_TYPE.PARAGRAPH)
        self.fig_caption.font.name = "Times New Roman"
        self.fig_caption.font.size = Pt(self.fig_cap_size)
        self.fig_caption.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # add styles
        self.my_table = self.styles.add_style("my_text", WD_STYLE_TYPE.TABLE)
        self.my_table.font.name = "Times New Roman"
        self.my_table.font.size = Pt(self.table_size)
        self.my_table.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

        self.heading_style = [self.styles.add_style("heading_{}".format(i), WD_STYLE_TYPE.PARAGRAPH) for i in range(3)]
        for i in range(3):
            self.heading_style[i].base_style = self.styles["Heading {}".format(i + 1)]
            self.heading_style[i].font.name = "Times New Roman"
            self.heading_style[i].font.size = Pt(self.heading_sizes[i])
            self.heading_style[i].font.color.theme_color = MSO_THEME_COLOR_INDEX.DARK_1
            self.heading_style[i].paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

        return

    def add_fig(self, filename, size, title):
        # add this figure
        self.num_fig += 1

        # add figure
        paragraph = self.doc.add_paragraph()
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = paragraph.add_run("")
        run.add_picture(filename, width=Cm(size[0] if size[0] < self.fig_x_max else self.fig_x_max))
        # add title
        self.doc.add_paragraph("Fig. {}. ".format(self.num_fig) + title, style=self.fig_caption)

        return

    def add_table(self, table_items):
        row, col = len(table_items), len(table_items[0])

        table = self.doc.add_table(rows=row, cols=col, style=self.my_table)
        for i in range(row):
            for j in range(col):
                table.cell(i, j).text = str(table_items[i][j])

        return

    def add_para(self, text):
        self.doc.add_paragraph(text, style=self.fig_caption)

    def add_heading(self, context, num):
        # add heading
        self.num_heading[num - 1] += 1

        self.doc.add_paragraph("{}. ".format(self.num_heading[num - 1]) + context, style=self.heading_style[num - 1])

    def __del__(self):
        # save the file
        self.doc.save(self.filename)


if __name__ == '__main__':
    docx = Document()
    docx.add_paragraph(" ")
    docx.save("./template.docx")

    docx = DocxFile("./data/test")

    docx.add_fig("./data/012_results/012_003_Blade_1_fx.png", (8, 4), "012_003_Blade_1_fx")
    docx.add_heading("./data/012_results/012_003_Blade_1_fx.png", 1)