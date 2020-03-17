import csv, math

# Assumes the information about the current semester is in a file called grades.csv
# File Structure Example
# course,units,grade
# courseA,4,8
# courseB,4,8
# courseC,4,10
#   .
#   .
#   .

current_gpa = float(input("Current GPA - "))
current_units = int(input("Current Units - "))
current_creds = math.ceil(current_gpa*current_units)

reader = csv.DictReader(open("grades.csv"))
units = 0
creds = 0
for row in reader:
    units += int(row["units"])
    creds += int(row["units"])*int(row["grade"])

sgpa = round(creds/units, 3)
gpa = round((current_creds + creds)/(current_units + units), 3)

print("-----------------------")
print("Calculated SGPA - {}".format(sgpa))
print("Calculated GPA - {}".format(gpa))