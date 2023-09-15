import pandas as pd
import sys

sys.path.append('c:\\Users\\navi\\Recuriter_selection_system\\data\\database')
from databaseConnection import save_to_database
sys.path.append('c:\\Users\\navi\\Recuriter_selection_system\\src')
from data_analysis.scraping import pushtoclean


def membership_period_conversion(data):
    years = data['Membership Period'].str.extract('(\d+) years').astype(float)
    months = data['Membership Period'].str.extract('(\d+) months').astype(float)
    years.fillna(0, inplace=True)
    months.fillna(0, inplace=True)
    data['Membership Period'] = (years + (months / 12)).round(1)
    return data
	
def process_data(raw_df): 
    skills = {
        "Python Developer": ["python", "django", "flask", "oop", "sql"],
        "C Developer": ["c", "memory management", "system programming", "debugging"],
        "C++ Developer": ["c++", "oop", "template programming", "qt"],
        "Java Developer": ["java", "spring", "hibernate", "jvm", "restful", "api"],
        "C# Developer": ["c#", ".net", "asp.net", "microsoft"],
        "JavaScript Developer": ["javascript", "es6", "react", "angular", "vue.js", "node.js", "asynchronous"],
        "SQL Developer": ["sql", "mysql", "postgresql", "oracle", "database design", "stored procedures", "triggers"],
        "R Developer": ["r", "dplyr", "tidyr", "statistical analysis", "ggplot2"],
        "Data Engineer": ["big data", "hadoop", "spark", "data warehousing", "sql", "nosql", "etl"],
        "Data Scientist": ["statistical analysis", "machine learning", "python", "r", "data visualization"],
        "Artificial Intelligence Specialist": ["machine learning", "deep learning", "tensorflow", "keras", "pytorch", "nlp", "reinforcement learning"],
        "Machine Learning Expert": ["machine learning", "scikit-learn", "tensorflow", "neural networks", "deep learning", "data preprocessing", "feature engineering"]
    }
    
    raw_df = membership_period_conversion(raw_df) 
    raw_df['Job Title'] = raw_df['Job Title'].fillna('Not Provided')
    
    tags_list = raw_df['User Tags'].str.split(' Score').apply(lambda x: [i.split()[-2].lower() for i in x[:-1]] if x else [])
    users_skills = {}
    for role, skill_set in skills.items():
        users_skills[role] = tags_list.apply(lambda x: any(skill in x for skill in skill_set))
    skills_df = pd.DataFrame(users_skills)
    skill_values = skills_df.astype(int)
    tag_values = pd.concat([raw_df, skill_values], axis=1)
    return tag_values

def main():
    raw_df = pushtoclean()
    processed_data = process_data(raw_df)

    processed_data['sequential_id'] = range(1, len(processed_data) + 1)
    #saving to the postgresql database
    save_to_database(processed_data) 

if __name__ == "__main__":
    main()
