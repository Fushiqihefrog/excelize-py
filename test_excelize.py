"""Copyright 2024 The excelize Authors. All rights reserved. Use of this source
code is governed by a BSD-style license that can be found in the LICENSE file.

Package excelize-py is a Python port of Go Excelize library, providing a set of
functions that allow you to write and read from XLAM / XLSM / XLSX / XLTM / XLTX
files. Supports reading and writing spreadsheet documents generated by Microsoft
Excel™ 2007 and later. Supports complex components by high compatibility, and
provided streaming API for generating or reading data from a worksheet with huge
amounts of data. This library needs Python version 3.9 or later.
"""

import excelize
import unittest
from dataclasses import dataclass
from unittest.mock import patch
import datetime
import random
from typing import List, Optional
from ctypes import (
    c_int,
    Structure,
    POINTER,
)
import os


class TestExcelize(unittest.TestCase):

    @patch("platform.architecture")
    def test_platform_architecture(self, mock_architecture):
        mock_architecture.return_value = ("unknown", "ELF")
        with self.assertRaises(SystemExit):
            excelize.load_lib()

    @patch("platform.machine")
    def test_platform_machine(self, mock_machine):
        mock_machine.return_value = "unknown"
        with self.assertRaises(SystemExit):
            excelize.load_lib()

    @patch("platform.machine")
    @patch("platform.system")
    def test_platform_machine_arm64(self, mock_machine, mock_system):
        mock_machine.return_value = "darwin"
        mock_system.return_value = "arm64"
        excelize.load_lib()

    @patch("platform.system")
    def test_platform_system(self, mock_system):
        mock_system.return_value = "unknown"
        with self.assertRaises(SystemExit):
            excelize.load_lib()

    def test_c_value_to_py(self):
        self.assertIsNone(excelize.c_value_to_py(None, None))

    def test_py_value_to_c(self):
        self.assertIsNone(excelize.py_value_to_c(None, None))

    def test_open_file(self):
        f, err = excelize.open_file("Book1.xlsx")
        self.assertIsNone(f)
        self.assertTrue(str(err).startswith("open Book1.xlsx"))

    def test_app_props(self):
        f = excelize.new_file()
        props, err = f.get_app_props()
        self.assertEqual(props.application, "Go Excelize")
        self.assertIsNone(err)

    def test_style(self):
        f = excelize.new_file()
        s = excelize.Style(
            border=[
                excelize.Border(type="left", color="0000FF", style=3),
                excelize.Border(type="right", color="FF0000", style=6),
                excelize.Border(type="top", color="00FF00", style=4),
                excelize.Border(type="bottom", color="FFFF00", style=5),
                excelize.Border(type="diagonalUp", color="A020F0", style=8),
                excelize.Border(type="diagonalDown", color="A020F0", style=8),
            ],
            font=excelize.Font(
                bold=True,
                size=11.5,
                italic=True,
                strike=True,
                color="FFF000",
                underline="single",
                family="Times New Roman",
                color_indexed=6,
                color_theme=1,
                color_tint=0.11,
            ),
            fill=excelize.Fill(shading=1, color=["00FF00", "FFFF00"], type="gradient"),
            alignment=excelize.Alignment(
                horizontal="center",
                indent=1,
                justify_last_line=True,
                reading_order=1,
                relative_indent=1,
                shrink_to_fit=True,
                text_rotation=180,
                vertical="center",
                wrap_text=True,
            ),
            protection=excelize.Protection(hidden=False, locked=True),
            custom_num_fmt=";;;",
        )
        style_id, err = f.new_style(s)
        self.assertIsNone(err)
        self.assertEqual(1, style_id)
        style, err = f.get_style(style_id)
        self.assertIsNone(err)
        self.assertEqual(style, s)
        self.assertIsNone(f.set_cell_style("Sheet1", "A1", "B2", style_id))
        self.assertEqual(
            str(f.set_cell_style("SheetN", "A1", "B2", style_id)),
            "sheet SheetN does not exist",
        )

        style, err = f.get_style(2)
        self.assertEqual("invalid style ID 2", str(err))
        self.assertIsNone(style)
        self.assertIsNone(f.save_as(os.path.join("test", "TestStyle.xlsx")))
        self.assertIsNone(
            f.save_as(os.path.join("test", "TestStyle.xlsx")),
            excelize.Options(password="password"),
        )
        self.assertIsNone(f.close())

        f, err = excelize.open_file(
            os.path.join("test", "TestStyle.xlsx"),
            excelize.Options(password="password"),
        )
        self.assertIsNone(err)
        with open("chart.png", "rb") as file:
            self.assertIsNone(
                f.set_sheet_background_from_bytes("Sheet1", ".png", file.read())
            )

        self.assertIsNone(f.set_cell_value("Sheet1", "A2", None))
        self.assertIsNone(f.set_cell_value("Sheet1", "A3", "Hello"))
        self.assertIsNone(f.set_cell_value("Sheet1", "A4", 100))
        self.assertIsNone(f.set_cell_value("Sheet1", "A5", 123.45))
        self.assertIsNone(f.set_cell_value("Sheet1", "A6", True))
        self.assertIsNone(
            f.set_cell_value("Sheet1", "A7", datetime.datetime(2016, 8, 30, 11, 51, 0))
        )
        self.assertIsNone(f.set_cell_value("Sheet1", "A8", datetime.date(2016, 8, 30)))
        self.assertIsNone(f.set_cell_bool("Sheet1", "A9", True))
        self.assertIsNone(f.set_cell_bool("Sheet1", "A10", False))
        self.assertEqual(
            str(f.set_cell_value("SheetN", "A9", None)),
            "sheet SheetN does not exist",
        )
        val, err = f.get_cell_value("Sheet1", "A2")
        self.assertEqual("", val)
        self.assertIsNone(err)

        val, err = f.get_cell_value("Sheet1", "A2")
        self.assertEqual("", val)
        self.assertIsNone(err)

        val, err = f.get_cell_value("Sheet1", "A3")
        self.assertEqual("Hello", val)
        self.assertIsNone(err)

        val, err = f.get_cell_value(
            "Sheet1", "A4", excelize.Options(raw_cell_value=True)
        )
        self.assertEqual("100", val)
        self.assertIsNone(err)

        self.assertIsNone(f.duplicate_row("Sheet1", 20))
        self.assertIsNone(f.duplicate_row_to("Sheet1", 20, 20))

        self.assertIsNone(f.merge_cell("Sheet1", "A1", "B2"))
        self.assertIsNone(f.unmerge_cell("Sheet1", "A1", "B2"))

        idx, err = f.new_sheet("Sheet2")
        self.assertEqual(idx, 1)
        self.assertIsNone(err)
        self.assertIsNone(f.set_active_sheet(idx))
        self.assertEqual(f.get_active_sheet_index(), idx)

        self.assertIsNone(f.set_col_outline_level("Sheet1", "D", 2))

        self.assertIsNone(f.set_sheet_background("Sheet2", "chart.png"))

        idx, err = f.new_sheet(":\\/?*[]Maximum 31 characters allowed in sheet title.")
        self.assertEqual(idx, -1)
        self.assertEqual(
            str(err), "the sheet name length exceeds the 31 characters limit"
        )

        idx, err = f.new_sheet("Sheet3")
        self.assertIsNone(err)
        self.assertIsNone(f.copy_sheet(1, idx))
        self.assertEqual(str(f.copy_sheet(1, 4)), "invalid worksheet index")

        self.assertIsNone(f.delete_sheet("Sheet3"))
        self.assertEqual(
            str(f.delete_sheet("Sheet:1")),
            "the sheet can not contain any of the characters :\\/?*[or]",
        )

        self.assertEqual(
            str(f.delete_chart("SheetN", "A1")), "sheet SheetN does not exist"
        )
        self.assertEqual(
            str(f.delete_comment("SheetN", "A1")), "sheet SheetN does not exist"
        )

        self.assertIsNone(f.delete_picture("Sheet1", "A1"))
        self.assertEqual(
            str(f.delete_comment("SheetN", "A1")), "sheet SheetN does not exist"
        )

        self.assertEqual(str(f.delete_slicer("x")), "slicer x does not exist")

        rows, err = f.get_rows("Sheet1")
        self.assertIsNone(err)
        self.assertEqual(
            rows,
            [
                ["Hello"],
                ["100"],
                ["123.45"],
                ["TRUE"],
                ["8/30/16 11:51"],
                ["08-30-16"],
                ["TRUE"],
                ["FALSE"],
            ],
        )
        rows, err = f.get_rows("Sheet1", excelize.Options(raw_cell_value=True))
        self.assertIsNone(err)
        self.assertEqual(
            rows,
            [
                ["Hello"],
                ["100"],
                ["123.45"],
                ["1"],
                ["42612.49375"],
                ["42612"],
                ["1"],
                ["0"],
            ],
        )

        self.assertIsNone(f.ungroup_sheets())
        self.assertIsNone(f.update_linked_value())
        self.assertIsNone(f.save())
        self.assertIsNone(f.save(excelize.Options(password="")))
        self.assertIsNone(f.close())

        with open(os.path.join("test", "TestStyle.xlsx"), "rb") as file:
            f, err = excelize.open_reader(file.read())
            self.assertIsNone(err)
            self.assertIsNone(f.save_as(os.path.join("test", "TestOpenReader.xlsx")))

        with open("chart.png", "rb") as file:
            _, err = excelize.open_reader(file.read(), excelize.Options(password=""))
            self.assertEqual(str(err), "zip: not a valid zip file")

    def test_add_chart(self):
        f = excelize.new_file()
        for idx, row in enumerate(
            [
                [None, "Apple", "Orange", "Pear"],
                ["Small", 2, 3, 3],
                ["Normal", 5, 2, 4],
                ["Large", 6, 7, 8],
            ]
        ):
            cell, err = excelize.coordinates_to_cell_name(1, idx + 1, False)
            self.assertIsNone(err)
            self.assertIsNone(f.set_sheet_row("Sheet1", cell, row))
        self.assertIsNone(
            f.add_chart(
                "Sheet1",
                "E1",
                chart=excelize.Chart(
                    type=excelize.ChartType.Col,
                    series=[
                        excelize.ChartSeries(
                            name="Sheet1!$A$2",
                            categories="Sheet1!$B$1:$D$1",
                            values="Sheet1!$B$2:$D$2",
                        ),
                        excelize.ChartSeries(
                            name="Sheet1!$A$3",
                            categories="Sheet1!$B$1:$D$1",
                            values="Sheet1!$B$3:$D$3",
                        ),
                        excelize.ChartSeries(
                            name="Sheet1!$A$4",
                            categories="Sheet1!$B$1:$D$1",
                            values="Sheet1!$B$4:$D$4",
                        ),
                    ],
                    title=[
                        excelize.RichTextRun(
                            text="Fruit 3D Clustered Column Chart",
                        )
                    ],
                ),
                combo=excelize.Chart(
                    type=excelize.ChartType.Line,
                    series=[
                        excelize.ChartSeries(
                            name="Sheet1!$A$2",
                            categories="Sheet1!$B$1:$D$1",
                            values="Sheet1!$B$2:$D$2",
                        ),
                        excelize.ChartSeries(
                            name="Sheet1!$A$3",
                            categories="Sheet1!$B$1:$D$1",
                            values="Sheet1!$B$3:$D$3",
                        ),
                        excelize.ChartSeries(
                            name="Sheet1!$A$4",
                            categories="Sheet1!$B$1:$D$1",
                            values="Sheet1!$B$4:$D$4",
                        ),
                    ],
                ),
            )
        )
        self.assertIsNone(
            f.add_chart_sheet(
                "Sheet2",
                chart=excelize.Chart(
                    type=excelize.ChartType.Col,
                    series=[
                        excelize.ChartSeries(
                            name="Sheet1!$A$2",
                            categories="Sheet1!$B$1:$D$1",
                            values="Sheet1!$B$2:$D$2",
                        ),
                        excelize.ChartSeries(
                            name="Sheet1!$A$3",
                            categories="Sheet1!$B$1:$D$1",
                            values="Sheet1!$B$3:$D$3",
                        ),
                        excelize.ChartSeries(
                            name="Sheet1!$A$4",
                            categories="Sheet1!$B$1:$D$1",
                            values="Sheet1!$B$4:$D$4",
                        ),
                    ],
                    title=[
                        excelize.RichTextRun(
                            text="Fruit 3D Clustered Column Chart",
                        )
                    ],
                ),
            )
        )
        self.assertIsNone(f.save_as(os.path.join("test", "TestAddChart.xlsx")))
        self.assertIsNone(f.close())

    def test_comment(self):
        f = excelize.new_file()
        self.assertIsNone(
            f.add_comment(
                "Sheet1",
                excelize.Comment(
                    cell="A5",
                    author="Excelize",
                    paragraph=[
                        excelize.RichTextRun(
                            text="Excelize: ",
                            font=excelize.Font(bold=True),
                        ),
                        excelize.RichTextRun(
                            text="This is a comment.",
                        ),
                    ],
                    height=40,
                    width=180,
                ),
            )
        )
        self.assertIsNone(f.save_as(os.path.join("test", "TestComment.xlsx")))
        self.assertIsNone(f.close())

    def test_add_form_control(self):
        f = excelize.new_file()
        self.assertIsNone(
            f.add_form_control(
                "Sheet1",
                excelize.FormControl(
                    cell="A3",
                    macro="Button1_Click",
                    width=140,
                    height=60,
                    text="Button 1\r\n",
                    paragraph=[
                        excelize.RichTextRun(
                            font=excelize.Font(
                                bold=True,
                                italic=True,
                                underline="single",
                                family="Times New Roman",
                                size=14,
                                color="777777",
                            ),
                            text="C1=A1+B1",
                        )
                    ],
                    type=excelize.FormControlType.FormControlButton,
                    format=excelize.GraphicOptions(
                        print_object=True,
                        positioning="absolute",
                    ),
                ),
            )
        )
        self.assertIsNone(
            f.add_form_control(
                "Sheet1",
                excelize.FormControl(
                    cell="A1",
                    text="Option Button 1",
                    type=excelize.FormControlType.FormControlOptionButton,
                ),
            )
        )
        self.assertIsNone(
            f.add_form_control(
                "Sheet1",
                excelize.FormControl(
                    cell="B1",
                    type=excelize.FormControlType.FormControlSpinButton,
                    width=15,
                    height=40,
                    current_val=7,
                    min_val=5,
                    max_val=10,
                    inc_change=1,
                    cell_link="A1",
                ),
            )
        )
        self.assertIsNone(
            f.add_form_control(
                "Sheet1",
                excelize.FormControl(
                    cell="B3",
                    type=excelize.FormControlType.FormControlScrollBar,
                    width=140,
                    height=20,
                    current_val=50,
                    min_val=10,
                    max_val=100,
                    page_change=1,
                    cell_link="A1",
                    horizontally=True,
                ),
            )
        )
        with open(os.path.join("test", "vbaProject.bin"), "rb") as file:
            self.assertIsNone(f.add_vba_project(file.read()))
        self.assertIsNone(f.save_as(os.path.join("test", "TestAddFormControl.xlsm")))
        self.assertIsNone(f.close())

    def test_pivot_table(self):
        f = excelize.new_file()
        month = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        year = [2017, 2018, 2019]
        types = ["Meat", "Dairy", "Beverages", "Produce"]
        region = ["East", "West", "North", "South"]
        self.assertIsNone(
            f.set_sheet_row(
                "Sheet1", "A1", ["Month", "Year", "Type", "Sales", "Region"]
            )
        )
        for row in range(2, 32):
            self.assertIsNone(
                f.set_cell_value("Sheet1", f"A{row}", month[random.randrange(12)])
            )
            self.assertIsNone(
                f.set_cell_value("Sheet1", f"B{row}", year[random.randrange(3)])
            )
            self.assertIsNone(
                f.set_cell_value("Sheet1", f"C{row}", types[random.randrange(4)])
            )
            self.assertIsNone(
                f.set_cell_value("Sheet1", f"D{row}", random.randrange(5000))
            )
            self.assertIsNone(
                f.set_cell_value("Sheet1", f"E{row}", region[random.randrange(4)])
            )
        self.assertIsNone(
            f.add_pivot_table(
                excelize.PivotTableOptions(
                    data_range="Sheet1!A1:E31",
                    pivot_table_range="Sheet1!G2:M34",
                    rows=[
                        excelize.PivotTableField(data="Month", default_subtotal=True),
                        excelize.PivotTableField(data="Year"),
                    ],
                    filter=[excelize.PivotTableField(data="Region")],
                    columns=[
                        excelize.PivotTableField(data="Type", default_subtotal=True),
                    ],
                    data=[
                        excelize.PivotTableField(
                            data="Sales", name="Summarize", subtotal="Sum"
                        ),
                    ],
                    row_grand_totals=True,
                    col_grand_totals=True,
                    show_drill=True,
                    show_row_headers=True,
                    show_col_headers=True,
                    show_last_column=True,
                )
            )
        )
        self.assertIsNone(f.save_as(os.path.join("test", "TestAddPivotTable.xlsx")))
        self.assertIsNone(f.close())

    def test_add_shape(self):
        f = excelize.new_file()
        self.assertIsNone(
            f.add_shape(
                "Sheet1",
                excelize.Shape(
                    cell="G6",
                    type="rect",
                    line=excelize.ShapeLine(
                        color="4286F4",
                        width=1.2,
                    ),
                    fill=excelize.Fill(
                        color=["8EB9FF"],
                        pattern=1,
                    ),
                    paragraph=[
                        excelize.RichTextRun(
                            text="Rectangle Shape",
                            font=excelize.Font(
                                bold=True,
                                italic=True,
                                family="Times New Roman",
                                size=19,
                                color="777777",
                                underline="sng",
                            ),
                        )
                    ],
                    width=180,
                    height=40,
                ),
            )
        )
        self.assertIsNone(f.save_as(os.path.join("test", "TestAddShape.xlsx")))
        self.assertIsNone(f.close())

    def test_add_slicer(self):
        f = excelize.new_file()
        self.assertIsNone(
            f.add_table(
                "Sheet1",
                excelize.Table(
                    name="Table1",
                    range="A1:D5",
                ),
            )
        )
        self.assertIsNone(
            f.add_slicer(
                "Sheet1",
                excelize.SlicerOptions(
                    name="Column1",
                    cell="E1",
                    table_sheet="Sheet1",
                    table_name="Table1",
                    caption="Column1",
                ),
            )
        )
        self.assertIsNone(f.save_as(os.path.join("test", "TestAddSlicer.xlsx")))
        self.assertIsNone(f.close())

    def test_add_sparkline(self):
        f = excelize.new_file()
        self.assertIsNone(
            f.add_sparkline(
                "Sheet1",
                excelize.SparklineOptions(
                    location=["A2"],
                    range=["Sheet1!B1:J1"],
                    markers=True,
                ),
            )
        )
        self.assertIsNone(f.save_as(os.path.join("test", "TestAddSparkline.xlsx")))
        self.assertIsNone(f.close())

    def test_auto_filter(self):
        f = excelize.new_file()
        self.assertIsNone(
            f.auto_filter(
                "Sheet1",
                "A2:D4",
                [],
            )
        )
        self.assertIsNone(
            f.auto_filter(
                "Sheet1",
                "F1:D4",
                [
                    excelize.AutoFilterOptions(
                        column="F",
                        expression="x != blanks",
                    )
                ],
            )
        )
        self.assertIsNone(f.save_as(os.path.join("test", "TestAutoFilter.xlsx")))
        self.assertIsNone(f.close())

    def test_calc_cell_formula(self):
        f = excelize.new_file()
        self.assertIsNone(f.set_sheet_row("Sheet1", "A1", [1, 2]))
        self.assertIsNone(f.set_cell_formula("Sheet1", "C1", "A1+B1"))
        formula, err = f.get_cell_formula("Sheet1", "C1")
        self.assertEqual(formula, "A1+B1")
        self.assertIsNone(err)
        self.assertIsNone(
            f.set_cell_formula(
                "Sheet1",
                "D1",
                "A1+B1",
                excelize.FormulaOpts(
                    type="shared",
                    ref="D1:D5",
                ),
            )
        )
        val, err = f.calc_cell_value("Sheet1", "C1")
        self.assertEqual(val, "3")
        self.assertIsNone(err)
        val, err = f.calc_cell_value("Sheet1", "D2")
        self.assertEqual(val, "0")
        self.assertIsNone(err)

    def test_cell_name_to_coordinates(self):
        col, row, err = excelize.cell_name_to_coordinates("Z3")
        self.assertEqual(col, 26)
        self.assertEqual(row, 3)
        self.assertIsNone(err)

        col, row, err = excelize.cell_name_to_coordinates("A")
        self.assertEqual(col, -1)
        self.assertEqual(row, -1)
        self.assertEqual(
            str(err),
            'cannot convert cell "A" to coordinates: invalid cell name "A"',
        )

    def test_cell_hyperlink(self):
        f = excelize.new_file()
        self.assertIsNone(f.set_cell_value("Sheet1", "A3", "HyperLink"))
        display = "https://github.com/xuri/excelize"
        self.assertIsNone(
            f.set_cell_hyperlink(
                "Sheet1",
                "A3",
                display,
                "External",
                excelize.HyperlinkOpts(display=display, tooltip="Excelize on GitHub"),
            )
        )
        # Set underline and font color style for the cell.
        style, err = f.new_style(
            excelize.Style(font=excelize.Font(color="1265BE", underline="single"))
        )
        self.assertIsNone(err)
        err = f.set_cell_style("Sheet1", "A3", "A3", style)
        self.assertIsNone(err)
        link, target, err = f.get_cell_hyperlink("Sheet1", "A3")
        self.assertTrue(link)
        self.assertEqual(target, display)
        self.assertIsNone(err)
        self.assertIsNone(f.save_as(os.path.join("test", "TestCellHyperLink.xlsx")))
        self.assertIsNone(f.close())

    def test_column_name_to_number(self):
        col, err = excelize.column_name_to_number("Z")
        self.assertEqual(col, 26)
        self.assertIsNone(err)

        col, err = excelize.column_name_to_number("-")
        self.assertEqual(col, -1)
        self.assertEqual(
            str(err),
            'invalid column name "-"',
        )

    def test_column_number_to_name(self):
        name, err = excelize.column_number_to_name(26)
        self.assertEqual(name, "Z")
        self.assertIsNone(err)

        name, err = excelize.column_number_to_name(0)
        self.assertEqual(name, "")
        self.assertEqual(
            str(err),
            "the column number must be greater than or equal to 1 and less than or equal to 16384",
        )

    def test_add_picture(self):
        f = excelize.new_file()
        self.assertIsNone(f.add_picture("Sheet1", "A1", "chart.png", None))
        self.assertIsNone(
            f.add_picture(
                "Sheet1",
                "A2",
                "chart.png",
                excelize.GraphicOptions(
                    print_object=True,
                    scale_x=0.1,
                    scale_y=0.1,
                    locked=False,
                ),
            )
        )
        with open("chart.png", "rb") as file:
            self.assertIsNone(
                f.add_picture_from_bytes(
                    "Sheet1",
                    "A3",
                    excelize.Picture(
                        extension=".png",
                        file=file.read(),
                        format=excelize.GraphicOptions(
                            print_object=True,
                            scale_x=0.1,
                            scale_y=0.1,
                            locked=False,
                        ),
                        insert_type=excelize.PictureInsertType.PictureInsertTypePlaceOverCells,
                    ),
                )
            )
        self.assertIsNone(f.save_as(os.path.join("test", "TestAddPicture.xlsx")))
        self.assertIsNone(f.close())

    def test_defined_name(self):
        f = excelize.new_file()
        self.assertIsNone(
            f.set_defined_name(
                excelize.DefinedName(
                    name="Amount",
                    refers_to="Sheet1!$A$2:$D$5",
                    comment="defined name comment",
                    scope="Sheet1",
                )
            )
        )
        self.assertIsNone(f.save_as(os.path.join("test", "TestSetDefinedName.xlsx")))
        self.assertIsNone(f.close())

    def test_sheet_view(self):
        f = excelize.new_file()
        expected = excelize.ViewOptions(
            default_grid_color=False,
            right_to_left=False,
            show_formulas=False,
            show_grid_lines=False,
            show_row_col_headers=False,
            show_ruler=False,
            show_zeros=False,
            top_left_cell="A1",
            view="normal",
            zoom_scale=120,
        )
        self.assertIsNone(f.set_sheet_view("Sheet1", 0, expected))
        self.assertIsNone(f.save_as(os.path.join("test", "TestSheetView.xlsx")))
        self.assertIsNone(f.close())

    def test_sheet_visible(self):
        f = excelize.new_file()
        _, err = f.new_sheet("Sheet2")
        self.assertIsNone(err)
        self.assertIsNone(f.set_sheet_visible("Sheet2", False, True))
        self.assertIsNone(f.save_as(os.path.join("test", "TestSheetVisible.xlsx")))
        self.assertIsNone(f.close())

    def test_workbook_props(self):
        f = excelize.new_file()
        expected = excelize.WorkbookPropsOptions(
            date1904=True, filter_privacy=True, code_name="code"
        )
        self.assertIsNone(f.set_workbook_props(expected))
        self.assertIsNone(f.save_as(os.path.join("test", "TestWorkbookProps.xlsx")))
        self.assertIsNone(f.close())

    def test_type_convert(self):
        class _T2(Structure):
            _fields_ = [
                ("D", c_int),
            ]

        class _T1(Structure):
            _fields_ = [
                ("ALen", c_int),
                ("A", POINTER(c_int)),
                ("BLen", c_int),
                ("B", POINTER(POINTER(c_int))),
                ("CLen", c_int),
                ("C", POINTER(POINTER(_T2))),
            ]

        @dataclass
        class T2:
            d: int = 0

        @dataclass
        class T1:
            a: Optional[List[int]] = None
            b: Optional[List[Optional[int]]] = None
            c: Optional[List[Optional[T2]]] = None

        t1 = T1(
            a=[1, 2, 3],
            b=[1, 2, 3],
            c=[T2(1), T2(2), T2(3)],
        )
        self.assertEqual(
            excelize.c_value_to_py(excelize.py_value_to_c(t1, _T1()), T1()), t1
        )
