# # Open xlsx file and extract data into csv file on linux
# import csv
# import openpyxl

# path = "edata.xlsx"
# wb = openpyxl.load_workbook(path)
# sheet = wb.active
# csv_file = open("edata.csv", "w")
# wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
# to_write = []

# for row in sheet.rows:
#     to_write.append([])
#     for cell in row:
#         if cell.value:
#             to_write[-1].append(cell.value)
#     if to_write[-1] == []:
#         to_write.pop(-1)
#     else:
#         # Write the whole row, including empty cells
#         wr.writerow([cell.value for cell in row])
        
# csv_file.close()