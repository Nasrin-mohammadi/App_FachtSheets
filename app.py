import sqlite3
import pandas as pd
import streamlit as st

# List of database file names
databases = {
    'Methods T1.2': 'Methods_T1.2.db',
    'Methods T1.3': 'Methods_T1.3.db',
    'Methods T1.4': 'Methods_T1.4.db',
    'Methods T2.1': 'Methods_T2.1.db',
    'Methods T2.2': 'Methods_T2.2.db',
    'Methods T2.4': 'Methods_T2.4.db'
}

def get_columns(sheet_name):
    """ Get the columns of a specific table. """
    db_name = databases.get(sheet_name)
    if not db_name:
        return None
    
    # Open a connection to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query just the first row to get column names
    cursor.execute(f'SELECT * FROM "{sheet_name}" LIMIT 1')
    columns = [description[0] for description in cursor.description]

    # Close the connection
    conn.close()

    return columns

def query_database(sheet_name, selected_columns=None, search_query=None):
    """ Query the database for all data or specific columns with search capability. """
    db_name = databases.get(sheet_name)
    if not db_name:
        return None
    
    # Open a connection to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Start building the query
    query = f'SELECT * FROM "{sheet_name}"'
    params = []

    # If search_query is provided
    if search_query:
        search_conditions = []

        # Check if "All Columns" is selected
        if selected_columns and 'All columns' not in selected_columns:
            # Only search in specified columns
            for col in selected_columns:
                search_conditions.append(f'"{col}" LIKE ?')
                params.append(f'%{search_query}%')
        else:
            # Search in all columns
            all_columns = get_columns(sheet_name)
            for col in all_columns:
                search_conditions.append(f'"{col}" LIKE ?')
                params.append(f'%{search_query}%')

        # Combine conditions with OR
        if search_conditions:
            query += ' WHERE ' + ' OR '.join(search_conditions)

    # Debugging output
    print("Query:", query)
    print("Params:", params)

    # Execute the query with parameters
    cursor.execute(query, params)

    # Fetch all results
    rows = cursor.fetchall()

    # Get the column names
    columns = [description[0] for description in cursor.description]

    # Convert the results to a DataFrame for better display
    df = pd.DataFrame(rows, columns=columns)

    # Filter based on selected columns if applicable
    if selected_columns and 'All columns' not in selected_columns:
        df = df[selected_columns]

    # Close the connection
    conn.close()

    return df

# Streamlit App Interface
def main():
    st.title("Methods Database Query App")

    # Sheet selection
    sheet_name = st.selectbox('Select a Methods Sheet', list(databases.keys()))

    # Get columns for the selected sheet
    columns = get_columns(sheet_name)
    columns.insert(0, 'All columns')  # Add 'All columns' option

    # Sidebar - Column Selection
    selected_columns = st.sidebar.multiselect('Select columns to display:', columns, default='All columns')
    search_query = st.sidebar.text_input('Enter search query:')

    # Fetch and display the selected columns
    if st.sidebar.button("Search"):
        df = query_database(sheet_name, selected_columns, search_query)
        if df is not None:
            if not df.empty:
                st.dataframe(df)

                # Prepare for download as CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="results.csv",
                    mime="text/csv",
                    key="download-csv"
                )
            else:
                st.write("No matching records found.")
        else:
            st.write("Error querying the database.")

if __name__ == "__main__":
    main()
