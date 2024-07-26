import ast
import re
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Helper functions
def convert_year(value):
    # Wandelt römische Zahlen in arabische um, Ausgabe nicht int, sondern str!
    def roman_to_int(roman):
        roman_values = {"M": 1000, "D": 500, "C": 100, 
                        "L": 50, "X": 10, "V": 5, "I": 1}
        
        total = 0
        prev_value = 0
        
        for char in reversed(roman):
            value = roman_values.get(char, 0)
            if value < prev_value:
                total -= value
            else:
                total += value
            prev_value = value
        
        return str(total)

    # Define a helper function to check if a string is a valid Roman numeral
    def is_roman_numeral(s):        
        # This regex pattern matches valid Roman numerals from 1 to 3999
        pattern = '^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,4})(IX|IV|V?I{0,4})$'
        
        return bool(re.match(pattern, s))
    
    original_value = value  # Keep the original value for debugging
    
    # Extract the first part if it contains additional information in brackets
    if "[" in value:
        match = re.search(r'\d{4}', value)
        if match:
            value = match.group(0)
        else:
            value = value.split("[")[0].strip()
    elif "-" in value:
        value = value.split("-")[0].strip()
    
    # Remove common non-Roman numeral prefixes
    value = re.sub(r'Im|Christi|De|Dato|Iahr|Den|Das', '', value, flags=re.IGNORECASE).strip()
    clean_value = ""
    
    match = re.search(r'\d{4}', value)
    if match:
        result = match.group(0)
    elif not value.isdigit():
        # Remove non-digit and non-Roman numeral characters
        clean_value = re.sub(r'[^IVXLCDM0-9]', '', value)
        if is_roman_numeral(clean_value):
            result = roman_to_int(clean_value)
        else:
            result = value
    
    # Debugging output
    if result == '0':
        print(f"Debug: original_value='{original_value}', clean_value='{clean_value}', result='{result}'")
    
    return result

# Säulendiagramm zu den haltenden Einrichtungen der gefundenen Werke
def location_graph(df):
    library_codes = df["Einrichtung"]
    
    library_list = []
    
    for element in library_codes:        
        if not isinstance(element, list):
            try:
                element = ast.literal_eval(element)
            except (ValueError, SyntaxError):
                continue
        for library in element:
            library_list.append(library)
    
    library_counts = pd.Series(library_list).value_counts()
    
    fig_loc = px.bar(library_counts, x=library_counts.index, y=library_counts.values,
                     labels={'x': 'Einrichtung', 'y': 'Count'},
                     title='Count of Works by Holding Institutions')
        
    return fig_loc

# Säulendiagramm zu den Veröffentlichungsjahren
def publication_date_graph(df):
    dates = df["Erscheinungsjahr"].apply(convert_year)
    date_counts = dates.value_counts(dropna=False).sort_index()
    
    fig_dates = px.bar(date_counts, x=date_counts.index, y=date_counts.values,
                       labels={'x': 'Erscheinungsjahr', 'y': 'Count'},
                       title='Count of Works by Publication Year')
    
    return fig_dates

# Säulendiagramm zu den Sprachen
def language_graph(df):
    language_codes = df["Sprache"]
    language_list = []
    
    for element in language_codes:        
        if not isinstance(element, list):
            try:
                element = ast.literal_eval(element)
            except (ValueError, SyntaxError):
                continue
        for language in element:
            language_list.append(language)
    
    language_counts = pd.Series(language_list).value_counts()
    
    fig_lang = px.bar(language_counts, x=language_counts.index, y=language_counts.values,
                      labels={'x': 'Sprache', 'y': 'Count'},
                      title='Count of Works by Language')
        
    return fig_lang

# Säulendiagramm zu den Sprachen über die Jahre
def language_year_graph(df):
    df['Cleaned_Year'] = df['Erscheinungsjahr'].apply(convert_year)
    
    # Split the 'Sprache' column into individual languages, clean them, and remove extraneous characters
    df['Sprache'] = df['Sprache'].apply(lambda x: [lang.strip("[]' ") for lang in x.split(',')])

    # Explode the 'Sprache' column into individual rows
    df_exploded = df.explode('Sprache')

    # Group by 'Cleaned_Year' and 'Sprache' and count the occurrences
    language_year_counts = df_exploded.groupby(['Cleaned_Year', 'Sprache']).size().reset_index(name='Count')

    fig_lang_year = px.line(language_year_counts, x='Cleaned_Year', y='Count', color='Sprache',
                            labels={'Cleaned_Year': 'Erscheinungsjahr', 'Count': 'Anzahl', 'Sprache': 'Sprache'},
                            title='Anzahl der verwendeten Sprachen über die Zeit')
    
    return fig_lang_year

pio.renderers.default = 'browser'

# Hier CSV-Datei einlesen lassen
df = pd.read_csv("DataFrame.csv")

fig_dates = publication_date_graph(df)
fig_dates.show()

fig_loc = location_graph(df)
fig_loc.show()

fig_lang = language_graph(df)
fig_lang.show()

fig_lang_year = language_year_graph(df)
fig_lang_year.show()
