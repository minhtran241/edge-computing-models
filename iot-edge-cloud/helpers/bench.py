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
                "Cloud": [43.1326, 0.0562],
                "Edge": [37.5978, 0.1524],  # Done
                "IoT Device": [220.9412, 0.1010],  # Done
            }
        },
        "Medium Size [500KB Input]": {
            "54 Iterations": {
                "Cloud": [143.8425, 0.0970],
                "Edge": [144.7311, 0.1627],  # Done
                "IoT Device": [894.8029, 0.1079],  # Done
            }
        },
        "Large Size [1.5MB Input]": {
            "54 Iterations": {
                "Cloud": [536.3999, 0.1748],
                # "Edge": [165.7513, 0.1204],
                # "IoT Device": [874.2084, 0.1178],
            }
        },
    },
    "Sentiment Analysis": {
        "Small Size [60 Reviews Input]": {
            "54 Iterations": {
                "Cloud": [10.9872, 0.1175],
                "Edge": [21.5537, 0.1935],
                "IoT Device": [166.8417, 0.0549],
            }
        },
        "Medium Size [200 Reviews Input]": {
            "54 Iterations": {
                "Cloud": [37.3203, 0.2778],
                "Edge": [70.0550, 0.3392],
                "IoT Device": [569.3127, 0.0550],
            }
        },
        "Large Size [1000 Reviews Input]": {
            "54 Iterations": {
                "Cloud": [188.8697, 1.2630],
                "Edge": [362.3646, 1.6529],
                "IoT Device": [2765.0394, 0.0546],
            }
        },
    },
    "Smith-Waterman": {
        "Small Size [25 KBs Input]": {
            "54 Iterations": {
                "Cloud": [12.8073, 0.0865],
                "Edge": [28.3816, 0.1397],
                "IoT Device": [212.8859, 0.0504],
            }
        },
        "Medium Size [50 KBs Input]": {
            "54 Iterations": {
                "Cloud": [38.6097, 0.1577],
                "Edge": [85.3803, 0.2060],
                "IoT Device": [683.7368, 0.0512],
            }
        },
        "Large Size [100 KBs Input]": {
            "54 Iterations": {
                "Cloud": [107.0593, 0.1870],
                "Edge": [233.5064, 0.2374],
                "IoT Device": [1908.5633, 0.0525],
            }
        },
    },
}

# Call the function to write data
write_xlsx("../bench/results.xlsx", data)
