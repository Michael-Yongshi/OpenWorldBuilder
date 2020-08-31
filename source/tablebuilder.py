import datetime

def create_owb_database(mainwindow, filename, path):

    handler = mainwindow.handler
    handler.database_new(filename=filename, path=path)

    get_normal_tables(handler)
    get_parent_tables(handler)
    get_fixed_parent_tables(handler)
    get_versionized_tables(handler)
    get_xreference_tables(handler)
    print(f"Tables added to database: {handler.database.tables}")

def get_normal_tables(handler):
    """
    TL;DR: child tables with the actual records / data

    normal tables or children tables

    i.e. create new characters, locations, events or story parts.
    """

    # Story
    handler.table_create(
        tablename = "stories",
        record_name = "story",
        column_names = ["summary", "body"],
        column_types = ["VARCHAR(255)", "TEXT"],
        column_placements = [
            # row, column, height, width
            [1,0,1,1],
            [2,0,1,1],
            [3,0,1,1],
            [4,0,10,1],
        ],
    )

    # Events
    handler.table_create(
        tablename = "events",
        column_names = ["date", "formatdate", "begin", "end", "description"],
        column_types = ["INTEGER", "VARCHAR(255)", "BOOL", "BOOL", "TEXT"],
        defaults = ["", 0, "", True, True, ""],
    )

    # Timelines
    handler.table_create(
        tablename = "timelines",
        column_names = ["description"],
        column_types = ["TEXT"],
    )
    
    # Locations
    handler.table_create(
        tablename = "locations",
        column_names = ["province_id", "description"],
        column_types = ["INTEGER REFERENCES provinces(id)", "TEXT"],
    )

    # Characters
    handler.table_create(
        tablename = "characters",
        column_names = ["age", "gender", "nationality", "culture", "race", "description"],
        column_types = ["INTEGER", "INTEGER REFERENCES FIXEDPARENT_genders(id)", "INTEGER REFERENCES countries(id)", "INTEGER REFERENCES cultures(id)", "INTEGER REFERENCES races(id)", "TEXT"],
    )

def get_parent_tables(handler):
    """
    TL;DR: Parent tables: one-to-many

    Parent tables are the records that can be referenced from the normal /child tables. 
    This is used to make changes to a group (record in the parent table) recursively for all children, without needing to change it for every child record.
    This can be both for a one-to-many relationship from parent to child as well as a many-to-many (versionized) relationship.

    i.e. a character has a race variable that is the same for other characters with the same race 
    giving them a real one-to-many relationship from this race (parent) table to the character (child) table
    makes it possible to change the description of the race attribute for all the characters in one go.
    """

    tables = []

    # # shown parent tables
    # Cultures
    handler.table_create(
        tablename = "cultures",
        column_names = ["description"],
        column_types = ["TEXT"],
    )

    # Races
    handler.table_create(
        tablename = "races",
        column_names = ["description"],
        column_types = ["TEXT"],
    )

    # Provinces
    handler.table_create(
        tablename = "provinces",
        column_names = ["description"],
        column_types = ["TEXT"],
    )

    # Countries (versionized)
    handler.table_create(
        tablename = "countries",
        record_name = "Country",
        column_names = ["description"],
        column_types = ["TEXT"],
    )

    # Empires (versionized)
    handler.table_create(
        tablename = "empires",
        column_names = ["description"],
        column_types = ["TEXT"],
    )

    # Magic
    handler.table_create(
        tablename = "magics",
        column_names = ["description"],
        column_types = ["TEXT"],
    )

    # Tech
    handler.table_create(
        tablename = "technologies",
        record_name= "technology",
        column_names = ["description"],
        column_types = ["TEXT"],
    )

    # Research
    handler.table_create(
        tablename = "research",
        column_names = ["description", "source"],
        column_types = ["TEXT", "VARCHAR(255)"],
    )

    return tables

def get_fixed_parent_tables(handler):
    """
    TL;DR: Parent tables: one-to-many fixed parent table

    Technically these are the same as normal parent tables, but these are assumed to be fixed / static
    These don't have to be changed by a regular user. they just have some initial values that can be used to 
    easily filter or make selections of the child tables.

    i.e. the values of genders, which are usually two and normally do not have to be changed.
    """

    # # not shown fixed parent tables
    gendertbl = handler.table_create(
        tablename = "FIXEDPARENT_genders",
        column_names = ["description"],
        column_types = ["TEXT"],
    )
    handler.table_create_add_records(
        tablename = gendertbl.name,
        recordsvalues = [
            [1, "Undetermined", "Undetermined"],
            [2, "Male", "Male"],
            [3, "Female", "Female"],
        ]
    )


def get_versionized_tables(handler):
    """
    TL;DR: Parent tables: many-to-many on a certain condition

    Versionized tables are cross referencing tables between a child and parent table. But instead of having a normal one-to-many relationship
    this parent and child are linked conditionally or versionized, which means that a many-to-many relationship is established.
    the child table has no foreign key directly to the parent table, but uses a version table to link to a parent on a certain condition
    (usually on time, but not exclusively).
    When referencing this table one can reference the record that is valid at that time (or for another certain condition). This is done by adding the first record
    with a start date and an empty end date. Whenever a new record is recorded for the same two children, the first record gets an end date and the added record a start date
    (with again an empty end date). Along this line you get different 'versions' of the same one-to-many relationship.

    i.e. an empire contains multiple countries in a one-to-many relationship (an empire has multiple countries in it, but a country can only belong to one empire at a time)
    , however in time new countries are conquered and other countries are lost. So depending on the time a country has different allegiances to different empires, 
    making it a many-to-many (versionized) table 
    or
    a character can only be in one place at a time, but over time this changes, making this a versionized many-to-many relationship on condition of time
    """

    handler.table_create(
        tablename = "VERSION_countries_provinces",
        column_names = ["startversion", "endversion", "country_id", "province_id", "description"],
        column_types = ["INTEGER", "INTEGER", "INTEGER REFERENCES countries(id)", "INTEGER REFERENCES provinces(id)", "TEXT"],
    )

    handler.table_create(
        tablename = "VERSION_empires_countries",
        column_names = ["startversion", "endversion", "empire_id", "country_id", "description"],
        column_types = ["INTEGER", "INTEGER", "INTEGER REFERENCES empires(id)", "INTEGER REFERENCES countries(id)", "TEXT"],
    )

def get_xreference_tables(handler):
    """
    TL;DR: child to child: many-to-many

    Many-to-many tables between two or more normal (children) tables, indicating that there are many different possible links in between two different records.
    These are many-to-many links that need to be mapped with an intermediate table containing just 2 foreign keys referencing 2 children tables.

    i.e. a character can be part of many different events, but an event can also have many participating / affected characters. Two link these two children tables
    we record every time a character plays in an event, creating a list of these occurences
    """

    # Creating this manually as its something linked to itself
    handler.table_create(
        tablename = "Relationships",
        column_names = ["character1_id", "character2_id", "description"],
        column_types = ["INTEGER REFERENCES characters(id)", "INTEGER REFERENCES characters(id)", "TEXT"],
    )

    # Stories to characters
    handler.crossref_create(
        tablename1="stories",
        tablename2="characters",
    )


# # Template
# handler.table_create(
#     tablename = "",
#     column_names = ["", ""],
#     column_types = ["", ""],
# )