import argparse
from datetime import date
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image, ImageFont, ImageDraw


ADDRESS = "411 East Ironwood Drive, West Monroe, LA"
COMPANY = "Frontier Roofing & Construction"
CONTACT = "daniel@frontierhomex.com"

ADDRESS_FONT = ImageFont.truetype("fonts/Lucida Grande.ttf", 36)
DATE_FONT = ImageFont.truetype("fonts/Lucida Grande.ttf", 32)
CONTACT_1_FONT = ImageFont.truetype("fonts/Lucida Grande.ttf", 32)
CONTACT_2_FONT = ImageFont.truetype("fonts/Lucida Grande.ttf", 20)
MEASUREMENTS_FONT = ImageFont.truetype("fonts/Lucida Grande.ttf", 20)
AREA_FONT = ImageFont.truetype("fonts/Lucida Grande Bold.ttf", 24)
LENGTHS_FONT = ImageFont.truetype("fonts/Lucida Grande.ttf", 24)
SUMMARY_FONT = ImageFont.truetype("fonts/Lucida Grande Bold.ttf", 24)

WASTE_PERCENTAGES = [
    1,
    1.1,
    1.12,
    1.15,
    1.17,
    1.2,
    1.22
]

def draw_underlined_text(draw, pos, text, font, color, **options):
    twidth, _ = draw.textsize(text, font=font)
    _, theight = draw.textsize("o", font=font)
    lx, ly = pos[0], pos[1] + theight + 3
    draw.text(pos, text, color, font=font, **options)
    draw.line((lx, ly, lx + twidth, ly), color, **options)
    return

def get_fit_image(img, bbox):
    bbox_w = bbox[1] - bbox[0]
    bbox_h = bbox[3] - bbox[2]

    bbox_aspect_ratio = bbox_w / bbox_h
    img_aspect_ratio = img.size[0] / img.size[1]

    if img_aspect_ratio > bbox_aspect_ratio:

        img_w = bbox_w
        img_h = int(bbox_w / img_aspect_ratio)

        pos = (bbox[0], bbox[2] + int(bbox_h / 2 - img_h / 2))

    else:
        img_h = bbox_h
        img_w = int(bbox_h * img_aspect_ratio)

        pos = (bbox[0] + int(bbox_w / 2 - img_w / 2), bbox[2])

    return img.resize((img_w, img_h)), pos

class ReportWriter:

    def __init__(
        self,
        folder,
        address,
        company,
        contact,
        measurements
    ):
        self.folder = folder
        self.address = address
        self.company = company
        self.contact = contact
        self.measurements = measurements
        return

    def add_header_to_img(self, img):
        draw = ImageDraw.Draw(img)

        w, h = ADDRESS_FONT.getsize(self.address)
        draw.text((1100 - w, 164), self.address, (255,255,255),
                  font=ADDRESS_FONT)

        _date = date.today().strftime("%B %d, %Y")

        w, h = DATE_FONT.getsize(_date)
        draw.text((1110 - w, 95), _date, (207,207,207),
                  font=DATE_FONT)

        return img

    def make_page_0(self):
        page = Image.open("report_page_templates/page_0.jpg")

        page = self.add_header_to_img(page)

        draw = ImageDraw.Draw(page)

        def fill_contact_box():
            draw_underlined_text(draw, (180, 1130), "Company:",
                                CONTACT_1_FONT, (0,0,0))

            draw_underlined_text(draw, (180, 1180), "Contact:",
                                CONTACT_1_FONT, (0,0,0))

            draw.text((350, 1138), self.company, (0,0,0), font=CONTACT_2_FONT)

            draw.text((320, 1187), self.contact, (0,0,0), font=CONTACT_2_FONT)

        def fill_key_measurements():
            x_pos, y_pos = 905, 778

            for i in range(8):
                if i == 0:
                    text = '{0:,.0f}'.format(self.measurements[i]) + " sq. ft."
                    draw.text((x_pos, y_pos), text, (0,0,0),
                            font=MEASUREMENTS_FONT)

                elif i > 2:
                    text = '{0:,}'.format(self.measurements[i]) + " ft."
                    draw.text((x_pos, y_pos), text, (0,0,0),
                            font=MEASUREMENTS_FONT)

                else:
                    text = str(self.measurements[i])
                    draw.text((x_pos, y_pos), text, (0,0,0),
                            font=MEASUREMENTS_FONT)


                y_pos += 30
                if i % 4 == 0:
                    y_pos += 1

        def add_image():
            box_left = 180
            box_right = 640
            box_top = 370
            box_bottom = 1040

            img = Image.open(os.path.join(self.folder, "top.png"))

            img, pos = get_fit_image(img, (box_left, box_right, box_top, box_bottom))

            page.paste(img, pos)

            return

        fill_contact_box()
        fill_key_measurements()
        add_image()

        return page

    def make_page_1(self):
        page = Image.open("report_page_templates/page_1.jpg")

        page = self.add_header_to_img(page)

        def add_image():
            box_left = 155
            box_right = 1110
            box_top = 385
            box_bottom = 1350

            img = Image.open(os.path.join(self.folder, "top.png"))

            img, pos = get_fit_image(img, (box_left, box_right, box_top, box_bottom))

            page.paste(img, pos)

            return

        add_image()

        return page

    def make_page_2(self):
        page = Image.open("report_page_templates/page_2.jpg")

        page = self.add_header_to_img(page)

        draw = ImageDraw.Draw(page)

        draw.text((952, 356),
                  '{0:,.0f}'.format(self.measurements[0]) + " sq. ft.",
                  (0,0,0), font=AREA_FONT)

        def add_image():
            box_left = 160
            box_right = 1110
            box_top = 425
            box_bottom = 1350

            img = Image.open(os.path.join(self.folder, "Area.png"))

            img, pos = get_fit_image(img, (box_left, box_right, box_top, box_bottom))

            page.paste(img, pos)

            return

        add_image()

        return page

    def make_page_3(self):
        page = Image.open("report_page_templates/page_3.jpg")

        page = self.add_header_to_img(page)

        draw = ImageDraw.Draw(page)

        def fill_length_table():
            COLORS = [
                (255,34,0),
                (255,136,0),
                (0,118,197),
                (69,163,38),
                (72,72,72)
            ]

            y_pos = 376

            for i in range(3,8):
                text = '{0:,}'.format(self.measurements[i])
                w, h = LENGTHS_FONT.getsize(text)

                draw.text((1026 - w / 2, y_pos), text,
                    COLORS[i-3], font=LENGTHS_FONT)

                y_pos += 38

        def add_image():
            box_left = 105
            box_right = 1110
            box_top = 570
            box_bottom = 1310

            img = Image.open(os.path.join(self.folder, "Length.png"))

            img, pos = get_fit_image(img, (box_left, box_right, box_top, box_bottom))

            page.paste(img, pos)

            return

        fill_length_table()
        add_image()

        return page

    def make_page_4(self):
        page = Image.open("report_page_templates/page_4.jpg")

        page = self.add_header_to_img(page)

        def add_image():
            box_left = 160
            box_right = 1110
            box_top = 385
            box_bottom = 1350

            img = Image.open(os.path.join(self.folder, "Pitch.png"))

            img, pos = get_fit_image(img, (box_left, box_right, box_top, box_bottom))

            page.paste(img, pos)

            return

        add_image()

        return page

    def make_page_5(self):
        page = Image.open("report_page_templates/page_5.jpg")

        page = self.add_header_to_img(page)

        def create_view_img():
            imgs = {
                "North": Image.open(self.folder+"/ims/north.png"),
                "East": Image.open(self.folder+"/ims/east.png"),
                "South": Image.open(self.folder+"/ims/south.png"),
                "West": Image.open(self.folder+"/ims/west.png")
            }

            min_w, min_h = float("inf"), float("inf")
            # Find the min width/height
            for img in imgs.values():
                min_w, min_h = min(min_w, img.size[0]), min(min_h, img.size[1])

            # Crop and save images
            final_imgs = dict.fromkeys(imgs.keys())

            for key, img in imgs.items():
                w, h = img.size
                m_w, m_h = (w - min_w) / 2, (h - min_h) / 2
                new = img.crop((
                    m_w,
                    m_h,
                    w - m_w,
                    h - m_h
                ))

                final_imgs[key] = new

            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2)
            ax1.imshow(final_imgs["North"])
            ax1.set_title("North Side")
            ax1.axis("off")

            ax2.imshow(final_imgs["South"])
            ax2.set_title("South Side")
            ax2.axis("off")

            ax3.imshow(final_imgs["East"])
            ax3.set_title("East Side")
            ax3.axis("off")

            ax4.imshow(final_imgs["West"])
            ax4.set_title("West Side")
            ax4.axis("off")

            plt.tight_layout()
            plt.savefig(os.path.join(self.folder, "views"), dpi=900)
            return

        def add_image():
            box_left = 155
            box_right = 1060
            box_top = 355
            box_bottom = 1380

            img = Image.open(os.path.join(self.folder, "views.png"))

            img, pos = get_fit_image(img, (box_left, box_right, box_top, box_bottom))

            page.paste(img, pos)

            return

        create_view_img()
        add_image()

        return page

    def make_page_6(self):
        page = Image.open("report_page_templates/page_6.jpg")

        page = self.add_header_to_img(page)

        draw = ImageDraw.Draw(page)

        def fill_pitch_and_area_table():
            table_left = 350
            table_right = 1080
            table_top = 442
            table_bottom = 530

            cols = len(self.measurements[8])

            col_lines_x = np.linspace(table_left, table_right, cols, endpoint=False)

            if cols > 1:
                half_col_w = int((col_lines_x[1] - table_left) / 2)
            else:
                half_col_w = int((table_right - table_left) / 2)

            for pitch, col_line_x in zip(self.measurements[8].keys(), col_lines_x):

                draw.line((col_line_x, table_top, col_line_x, table_bottom), fill=0, width=2)

                x_pos = col_line_x + half_col_w

                pitch_text = '{0:,.0f}'.format(pitch)
                area_text = '{0:,.0f}'.format(self.measurements[8][pitch])
                percent_text = str(int(100 * self.measurements[8][pitch] / self.measurements[0])) + "%"

                draw.text((x_pos - SUMMARY_FONT.getsize(pitch_text)[0] / 2, 449), pitch_text, (0,0,0), font=SUMMARY_FONT)
                draw.text((x_pos - SUMMARY_FONT.getsize(area_text)[0] / 2, 479), area_text, (0,0,0), font=SUMMARY_FONT)
                draw.text((x_pos - SUMMARY_FONT.getsize(percent_text)[0] / 2, 509), percent_text, (0,0,0), font=SUMMARY_FONT)

            return

        def fill_waste_table():
            area = self.measurements[0]

            x_pos = 330
            spacing = 115

            for waste_percentage in WASTE_PERCENTAGES:
                curr_area = area * waste_percentage
                area_text = '{0:,.0f}'.format(curr_area)
                square_text = '{0:.1f}'.format(curr_area / 100)

                draw.text((x_pos - SUMMARY_FONT.getsize(area_text)[0] / 2, 731), area_text, (0,0,0), font=SUMMARY_FONT)
                draw.text((x_pos - SUMMARY_FONT.getsize(square_text)[0] / 2, 762), square_text, (0,0,0), font=SUMMARY_FONT)

                x_pos += spacing

            return

        def fill_length_table():
            x_pos = 391
            y_pos = 997
            x_spacing = 153

            for i in range(3,8):
                length_text = '{0:,}'.format(self.measurements[i])

                draw.text((x_pos - SUMMARY_FONT.getsize(length_text)[0] / 2, y_pos), length_text, (0,0,0), font=SUMMARY_FONT)

                x_pos += x_spacing

            return


        fill_pitch_and_area_table()
        fill_waste_table()
        fill_length_table()

        return page

    def create_report(self):
        filename = os.path.join(self.folder+"/report.pdf")

        cover_img = self.make_page_0()

        page_imgs = [
            self.make_page_1(),
            self.make_page_2(),
            self.make_page_3(),
            self.make_page_4(),
            self.make_page_5(),
            self.make_page_6()
        ]

        cover_img.save(filename, "PDF", resolution=200.0,
                       save_all=True, append_images=page_imgs)

        return





