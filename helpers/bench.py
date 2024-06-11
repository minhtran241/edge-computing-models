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

    # Write data for each data set
    for table_name, table_data in data.items():
        current_row = write_table_name(ws, current_row, table_name)
        current_row = write_headers(ws, current_row)
        for iteration_label, iteration_data in table_data.items():
            current_row = write_data(ws, current_row, iteration_label, iteration_data)

    # Close the workbook
    wb.close()


# Define the data structure
small_data = {
    "OCR [100 KBs Input]": {
        "25 Iterations": {
            "Cloud": [10.6739, 0.0362],
            "Edge": [34.8822, 0.1895],
            "IoT Device": [70.7723, 0.0497],
        },
    },
    "Sentiment Analysis [60 Reviews Input]": {
        "25 Iterations": {
            "Cloud": [5.2869, 0.0741],
            "Edge": [29.7432, 0.2562],
            "IoT Device": [77.5999, 0.0258],
        }
    },
    "Smith-Waterman [25 KBs Input]": {
        "25 Iterations": {
            "Cloud": [6.0341, 0.0510],
            "Edge": [36.7821, 0.2696],
            "IoT Device": [99.3482, 0.0231],
        },
    },
}

medium_data = {
    "Sentiment Analysis [200 Reviews Input]": {
        "25 Iterations": {
            "Cloud": [17.1651, 0.1543],
            "Edge": [99.8172, 0.5227],
            "IoT Device": [264.7352, 0.0265],
        }
    },
    "Smith-Waterman [50 KBs Input]": {
        "25 Iterations": {
            "Cloud": [18.5464, 0.0741],
            "Edge": [117.1889, 0.2750],
            "IoT Device": [314.7858, 0.0240],
        },
    },
}

large_data = {
    "OCR [1 MB Input]": {
        "25 Iterations": {
            "Cloud": [87.4087, 0.0842],
            "Edge": [227.6826, 0.2861],
            "IoT Device": [447.2824, 0.0588],
        },
    },
    "Sentiment Analysis [1000 Reviews Input]": {
        "25 Iterations": {
            "Cloud": [86.0777, 0.5098],
            "Edge": [501.7732, 2.0292],
            "IoT Device": [1321.7730, 0.0248],
        }
    },
    "Smith-Waterman [100 KBs Input]": {
        "25 Iterations": {
            "Cloud": [51.4267, 0.1115],
            "Edge": [307.9444, 0.2861],
            "IoT Device": [853.5634, 0.0270],
        },
    },
}

# Call the function to write data
write_xlsx("../bench/small.xlsx", small_data)
write_xlsx("../bench/medium.xlsx", medium_data)
write_xlsx("../bench/large.xlsx", large_data)
