import pandas as pd
import random
import argparse

def replacing_values(x, count, values):
    if count > (len(values)*10):
        return x
    else:
        count += 1
        return values[random.randint(0, len(values)-1)]


def adding_race_concepts(person_table):
    values = ["8657","8515","8557", "8516", "8527"]
    count = 0

    data = pd.read_csv(person_table)
    #print (data[["person_id", "gender_concept_id", "race_concept_id"]])
    data["race_concept_id"] = data["race_concept_id"].apply(lambda x: replacing_values(x, count, values))
    data = data[["person_id","gender_concept_id","year_of_birth","month_of_birth","day_of_birth","time_of_birth","race_concept_id","ethnicity_concept_id","location_id","provider_id","care_site_id","person_source_value","gender_source_value","gender_source_concept_id","race_source_value","race_source_concept_id","ethnicity_source_value","ethnicity_source_concept_id"]]
    #print (data[["person_id", "gender_concept_id", "race_concept_id"]])
    data.to_csv(person_table, index=False)
    #exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--person_file", required=True, help="Path to the person.csv file")
    args = parser.parse_args()

    
    adding_race_concepts(args.person_file)