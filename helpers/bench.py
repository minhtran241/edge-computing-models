import xlsxwriter


# Function to write data to the worksheet
def write_xlsx(workbook_path, data):
    wb = xlsxwriter.Workbook(workbook_path)
    ws = wb.add_worksheet()

    # Write the headers
    headers = [
        "Iteration",
        "Computing Model",
        "Processing Time (Sec)",
        "Transmission Time (Sec)",
        "Total Finishing Time (Sec)",
    ]

    def write_table_name(sheet, row, table_name):
        sheet.write(row, 0, table_name)
        return row + 1

    def write_headers(sheet, row):
        for col_num, header in enumerate(headers):
            sheet.write(row, col_num, header)
        return row + 1

    # Function to write data for each iteration
    def write_data(sheet, start_row, iteration_label, iteration_data):
        row = start_row
        for model, times in iteration_data.items():
            processing_time = times[0]
            transmission_time = times[1]
            total_time = processing_time + transmission_time

            sheet.write(row, 0, iteration_label)
            sheet.write(row, 1, model)
            sheet.write(row, 2, processing_time)
            sheet.write(row, 3, transmission_time)
            sheet.write(row, 4, total_time)
            row += 1
        return row + 1

    # Start writing data
    current_row = 0

    # Write data for each dataset
    for dataset_name, data in data.items():
        for table_name, table_data in data.items():
            current_row = write_table_name(
                ws, current_row, f"{dataset_name} - {table_name}"
            )
            current_row = write_headers(ws, current_row)
            for iteration_label, iteration_data in table_data.items():
                current_row = write_data(
                    ws, current_row, iteration_label, iteration_data
                )

    # Close the workbook
    wb.close()


data = {
    "OCR": {
        "Small Size [100 KBs Input]": {
            "24 Iterations": {
                "Cloud": [9.7870, 0.0535],
                "Edge": [11.2323, 0.0291],
                "IoT Device": [67.7799, 0.0480],
            }
        },
        "Medium Size [500 KBs Input]": {
            "24 Iterations": {
                "Cloud": [16.3796, 0.1615],
                "Edge": [31.7640, 0.0697],
                "IoT Device": [247.5658, 0.0248],
            }
        },
        "Large Size [1000 KBs Input]": {
            "24 Iterations": {
                "Cloud": [82.8394, 0.1003],
                "Edge": [73.3697, 0.0705],
                "IoT Device": [429.5356, 0.0525],
            }
        },
    },
    "Sentiment Analysis": {
        "Small Size [60 Reviews Input]": {
            "24 Iterations": {
                "Cloud": [4.8666, 0.0795],
                "Edge": [9.5607, 0.0286],
                "IoT Device": [74.2696, 0.0242],
            }
        },
        "Medium Size [200 Reviews Input]": {
            "24 Iterations": {
                "Cloud": [16.3796, 0.1615],
                "Edge": [31.7640, 0.0697],
                "IoT Device": [247.5658, 0.0248],
            }
        },
        "Large Size [1000 Reviews Input]": {
            "24 Iterations": {
                "Cloud": [81.5103, 0.5251],
                "Edge": [162.0461, 0.2048],
                "IoT Device": [1228.7675, 0.0258],
            }
        },
    },
    "Smith-Waterman": {
        "Small Size [25 KBs Input]": {
            "24 Iterations": {
                "Cloud": [5.6920, 0.0649],
                "Edge": [12.0487, 0.0407],
                "IoT Device": [96.2786, 0.0224],
            }
        },
        "Medium Size [50 KBs Input]": {
            "24 Iterations": {
                "Cloud": [17.4616, 0.0763],
                "Edge": [38.2603, 0.0384],
                "IoT Device": [304.2836, 0.0226],
            }
        },
        "Large Size [100 KBs Input]": {
            "24 Iterations": {
                "Cloud": [48.4401, 0.1071],
                "Edge": [107.4908, 0.0383],
                "IoT Device": [832.6830, 0.0228],
            }
        },
    },
}

# Call the function to write data
write_xlsx("../bench/results.xlsx", data)
