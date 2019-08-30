import pandas as pd
import random
import argparse

def replacing_values(x, count, values):
    if count > (len(values)*10):
        return x
    else:
        count += 1
        return values[random.randint(0, 2)]


def adding_race_concepts(person_table):
    values = ["8657","8515","8557", "8516", "8527"]
    count = 0

    data = pd.read_csv(person_table)
    #print (data[["person_id", "gender_concept_id", "race_concept_id"]])
    data["race_concept_id"] = data["race_concept_id"].apply(lambda x: replacing_values(x, count, values))
    #print (data[["person_id", "gender_concept_id", "race_concept_id"]])
    data.to_csv(person_table)
    #exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--person_file", required=True, help="Path to the person.csv file")
    args = parser.parse_args()

    
    adding_race_concepts(args.person_file)