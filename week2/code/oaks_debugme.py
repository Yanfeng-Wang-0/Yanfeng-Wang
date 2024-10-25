import csv
import sys

# Define function
def is_an_oak(name):
    """ Returns True if the name starts with 'quercus' """
    return name.lower().startswith('quercus')

def main(argv): 
    # Use context managers to open files
    with open('../data/TestOaksData.csv', 'r') as f, open('../data/JustOaksData.csv', 'w', newline='') as g:
        taxa = csv.reader(f)
        csvwrite = csv.writer(g)
        oaks = set()

        for row in taxa:
            if is_an_oak(row[0]):
                print(f'FOUND AN OAK: {row[0]}')
                oaks.add(row[0])  # Optionally keep track of unique oaks
                csvwrite.writerow([row[0], row[1]])    

if __name__ == "__main__":
    main(sys.argv)
