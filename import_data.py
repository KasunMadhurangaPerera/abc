import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DECIMAL, text
from sqlalchemy.exc import SQLAlchemyError

# Database connection parameters
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'VALUATION'

# CSV file path
data_file = 'C:\\Users\\Perera KKM\\Desktop\\New folder (4)\\valuation\\data.csv'

try:
    engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}', echo=False)
    metadata = MetaData()

    vehicles_table = Table('vehicles', metadata,
        Column('vehicle_id', Integer, primary_key=True, autoincrement=True),
        Column('brand', String(255), nullable=False),
        Column('model', String(255), nullable=False),
        Column('year_of_manufacture', Integer, nullable=False),
        Column('year_month', String(7), nullable=False),
        Column('price', DECIMAL(12, 2), nullable=False),
        Column('engine_capacity', String(50), nullable=False),
        Column('transmission', String(50), nullable=False),
        Column('fuel_type', String(50), nullable=False),
        Column('mileage', Float, nullable=False)
    )

    metadata.create_all(engine)

    with engine.connect() as conn:
        row_count = conn.execute(text("SELECT COUNT(*) FROM vehicles")).scalar()
        if row_count == 0:
            car_df = pd.read_csv(data_file)
            car_df.columns = car_df.columns.str.strip()

            # Drop rows with missing values
            car_df.dropna(inplace=True)

            # Ensure numeric 'price' and filter out invalid values
            car_df['price'] = pd.to_numeric(car_df['price'], errors='coerce')
            car_df = car_df[car_df['price'] <= 9999999999.99]

            # Clean mileage
            car_df['mileage'] = car_df['mileage'].str.replace(',', '').str.replace(' km', '', regex=False).astype(float)

            # Convert yymm to year_month
            car_df['year_month'] = car_df['yymm'].astype(str).str.zfill(4).apply(lambda x: f"{x[:2]}/{x[2:]}")
            car_df.drop(columns=['yymm'], inplace=True)

            car_df.to_sql('vehicles', con=engine, if_exists='append', index=False)
            print("Data imported successfully.")
        else:
            print("Data already exists in the table.")

except SQLAlchemyError as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Error: {e}")
