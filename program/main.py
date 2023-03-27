import yaml
import json
import sqlite3
from tkinter import *
import os


class Record:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class App:
    def __init__(self, master, config_file):
        # Initialize the App object with a Tkinter master object and a configuration file
        self.master = master
        self.config_file = config_file
        # Initialize an empty list to store the Record objects
        self.records = []
        # Load the fields from the configuration file
        self.fields = self.load_fields_from_config()
        # Create the GUI widgets
        self.create_widgets()

    # Load the fields from the configuration file
    def load_fields_from_config(self):
        with open(os.path.join(os.path.dirname(__file__), self.config_file)) as f:
            config = yaml.safe_load(f)
        return config['fields']

    # Create the GUI widgets
    def create_widgets(self):
        # For each field in the fields list, create a Label and Entry widget for input
        for field in self.fields:
            label = Label(self.master, text=field['label'])
            label.pack(side=TOP)
            setattr(self, field['name'], Entry(self.master))
            getattr(self, field['name']).pack(side=TOP)
        save_button = Button(self.master, text='Save', command=self.save_record)
        save_button.pack(side=LEFT)
        exit_button = Button(self.master, text='Exit', command=self.exit_app)
        exit_button.pack(side=LEFT)

    # Save the record to memory
    def save_record(self):
        record_data = {}
        # For each field in the fields list, get the value from the Entry widget and delete the contents
        for field in self.fields:
            record_data[field['name']] = getattr(self, field['name']).get()
            getattr(self, field['name']).delete(0, END)
        # Create a Record object with the field values and add it to the records list
        record = Record(**record_data)
        self.records.append(record)

    def exit_app(self):
        output_file = self.load_output_file_from_config()
        self.write_to_json(output_file)
        db_file, table_name = self.load_db_info_from_config()
        self.write_to_sqlite(db_file, table_name)
        self.master.quit()

    def load_output_file_from_config(self):
        with open(os.path.join(os.path.dirname(__file__), self.config_file)) as f:
            config = yaml.safe_load(f)
        db_file = os.path.realpath(os.path.join(os.path.dirname(__file__), config['output']['file']))
        return db_file

    def write_to_json(self, test_output):
        data = [record.__dict__ for record in self.records]
        with open(test_output, 'w') as f:
            json.dump(data, f)

    def load_db_info_from_config(self):
        with open(os.path.join(os.path.dirname(__file__), self.config_file)) as f:
            config = yaml.safe_load(f)
        db_file = os.path.realpath(os.path.join(os.path.dirname(__file__), config['database']['file']))
        table_name = config['database']['table']
        return db_file, table_name

    def write_to_sqlite(self, db_file, table_name):
        try:
            with open(db_file, 'w+'):
                conn = sqlite3.connect(db_file)
            c = conn.cursor()
            # Create table if it does not exist
            c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({','.join([field['name'] + ' TEXT' for field in self.fields])})")
            # Insert records
            for record in self.records:
                values = tuple(getattr(record, field['name']) for field in self.fields)
                c.execute(f"INSERT INTO {table_name} VALUES ({','.join(['?' for field in self.fields])})", values)
            conn.commit()
        except Exception as e:
            print(f"Error writing to database: {e}")
        finally:
            conn.close()


if __name__ == '__main__':
    root = Tk()
    app = App(root, 'config.yml')
    root.mainloop()
