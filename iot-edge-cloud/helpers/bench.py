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
        "Small Size [11KB Input]": {
            "54 Iterations": {
                "Cloud": [8.2173, 0.1495],  # Done
                # "Edge": [25.2146, 0.0557],
                "IoT Device": [86.6929, 0.1628],
            }
        },
        "Medium Size [500KB Input]": {
            "54 Iterations": {
                "Cloud": [176.2718, 0.1582],  # Done
                # "Edge": [144.5870, 0.0961],
                "IoT Device": [881.1115, 0.1827],
            }
        },
        "Large Size [1.5MB Input]": {
            "54 Iterations": {
                "Cloud": [177.9795, 0.1616],  # Done
                # "Edge": [165.7513, 0.1204],
                "IoT Device": [874.2084, 0.1178],
            }
        },
    },
    "Sentiment Analysis": {
        "Small Size [60 Reviews Input]": {
            "54 Iterations": {
                "Cloud": [11.4662, 0.4190],  # Done
                # "Edge": [21.3208, 0.1480],
                "IoT Device": [146.1732, 0.0904],  # Done
            }
        },
        "Medium Size [200 Reviews Input]": {
            "54 Iterations": {
                "Cloud": [38.5115, 1.6901],  # Done
                # "Edge": [72.1063, 0.3695],
                "IoT Device": [554.8186, 0.1095],  # Done
            }
        },
        "Large Size [1000 Reviews Input]": {
            "54 Iterations": {
                "Cloud": [189.8607, 11.6505],  # Done
                # "Edge": [358.7299, 1.2207],
                "IoT Device": [2781.0971, 0.1013],  # Done
            }
        },
    },
    "Smith-Waterman": {
        "Small Size [25 KBs Input]": {
            "54 Iterations": {
                "Cloud": [12.9886, 0.1937],  # Done
                # "Edge": [27.0720, 0.1543],
                "IoT Device": [218.6766, 0.0923],  # Done
            }
        },
        "Medium Size [50 KBs Input]": {
            "54 Iterations": {
                "Cloud": [40.3823, 0.5989],  # Done
                # "Edge": [38.2603, 0.0384],
                "IoT Device": [684.0986, 0.0960],  # Done
            }
        },
        "Large Size [100 KBs Input]": {
            "54 Iterations": {
                "Cloud": [110.3009, 1.6136],  # Done
                # "Edge": [107.4908, 0.0383],
                "IoT Device": [1838.5679, 0.0975],  # Done
            }
        },
    },
}

# Call the function to write data
write_xlsx("../bench/results.xlsx", data)
