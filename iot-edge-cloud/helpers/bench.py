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
        "Small Size [11KB Input]": {  # Done
            "54 Iterations": {
                "Cloud": [7.9265, 0.1118],
                # "Edge": [25.2146, 0.0557],
                "IoT Device": [94.5099, 0.0996],
            }
        },
        "Medium Size [500KB Input]": {
            "54 Iterations": {
                "Cloud": [146.4107, 0.1242],
                # "Edge": [144.5870, 0.0961],
                "IoT Device": [826.4992, 0.1132],
            }
        },
        "Large Size [1.5MB Input]": {  # Done
            "54 Iterations": {
                "Cloud": [146.4495, 0.1677],
                # "Edge": [165.7513, 0.1204],
                "IoT Device": [874.2084, 0.1178],
            }
        },
    },
    "Sentiment Analysis": {
        "Small Size [60 Reviews Input]": {
            "54 Iterations": {
                "Cloud": [11.0045, 0.1036],
                # "Edge": [21.3208, 0.1480],
                "IoT Device": [146.1104, 0.0509],
            }
        },
        "Medium Size [200 Reviews Input]": {
            "54 Iterations": {
                "Cloud": [37.0548, 0.2493],
                # "Edge": [72.1063, 0.3695],
                "IoT Device": [538.8425, 0.0520],
            }
        },
        "Large Size [1000 Reviews Input]": {
            "54 Iterations": {
                "Cloud": [183.0799, 1.1436],
                # "Edge": [358.7299, 1.2207],
                "IoT Device": [2812.2925, 0.0535],
            }
        },
    },
    "Smith-Waterman": {
        "Small Size [25 KBs Input]": {
            "54 Iterations": {
                "Cloud": [12.5588, 0.0660],
                # "Edge": [27.0720, 0.1543],
                "IoT Device": [216.5213, 0.0509],
            }
        },
        "Medium Size [50 KBs Input]": {
            "54 Iterations": {
                "Cloud": [39.0103, 0.1342],
                # "Edge": [38.2603, 0.0384],
                "IoT Device": [676.6986, 0.0555],
            }
        },
        "Large Size [100 KBs Input]": {
            "54 Iterations": {
                "Cloud": [07.1914, 0.1646],
                # "Edge": [107.4908, 0.0383],
                "IoT Device": [1838.2641, 0.0580],
            }
        },
    },
}

# Call the function to write data
write_xlsx("../bench/results.xlsx", data)
