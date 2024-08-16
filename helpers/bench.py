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
            "25 Iterations": {
                "Cloud": [6.5443, 0.0870],
                # "Edge": [25.2146, 0.0557],
                "IoT Device": [5.8672, 0.0791],
            }
        },
        "Medium Size [100KB Input]": {
            "25 Iterations": {
                "Cloud": [21.7135, 0.0743],
                # "Edge": [144.5870, 0.0961],
                "IoT Device": [70.4520, 0.0870],
            }
        },
        "Large Size [1.5MB Input]": {  # Done
            "25 Iterations": {
                "Cloud": [188.6251, 0.1666],
                # "Edge": [165.7513, 0.1204],
                "IoT Device": [410.5571, 0.0927],
            }
        },
    },
    "Sentiment Analysis": {
        "Small Size [60 Reviews Input]": {  # Done
            "54 Iterations": {
                "Cloud": [23.1357, 0.1655],
                # "Edge": [21.3208, 0.1480],
                "IoT Device": [152.7544, 0.0522],
            }
        },
        "Medium Size [200 Reviews Input]": {  # Done
            "54 Iterations": {
                "Cloud": [40.6018, 0.2960],
                # "Edge": [72.1063, 0.3695],
                "IoT Device": [565.6999, 0.0539],
            }
        },
        "Large Size [1000 Reviews Input]": {  # Done
            "54 Iterations": {
                "Cloud": [371.7102, 1.1002],
                # "Edge": [358.7299, 1.2207],
                "IoT Device": [2802.7010, 0.0563],
            }
        },
    },
    "Smith-Waterman": {
        "Small Size [25 KBs Input]": {  # Done
            "54 Iterations": {
                "Cloud": [26.1891, 0.1453],
                # "Edge": [27.0720, 0.1543],
                "IoT Device": [195.6620, 0.0566],
            }
        },
        "Medium Size [50 KBs Input]": {  # Done
            "54 Iterations": {
                "Cloud": [156.0036, 0.1611],
                # "Edge": [38.2603, 0.0384],
                "IoT Device": [678.9911, 0.0581],
            }
        },
        "Large Size [100 KBs Input]": {
            "54 Iterations": {
                "Cloud": [239.9267, 0.2140],
                # "Edge": [107.4908, 0.0383],
                "IoT Device": [1881.4924, 0.0602],
            }
        },
    },
}

# Call the function to write data
write_xlsx("../bench/results.xlsx", data)
