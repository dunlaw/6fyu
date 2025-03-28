# Property Tycoon Loadexcel.py
# It contains the classes for loading the property data, the game text, and the card data.

import pandas as pd
import os


def load_property_data(filename="assets/gamedata/PropertyTycoonBoardData.xlsx"):
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(current_dir, filename)
        print(f"Loading property data from: {file_path}")

        if not os.path.exists(file_path):
            print(f"File not found at {file_path}")
            alt_path = os.path.join(
                current_dir, "Useful Canvas file", "PropertyTycoonBoardData.xlsx"
            )
            if os.path.exists(alt_path):
                file_path = alt_path
                print(f"Using alternative path: {alt_path}")
            else:
                raise FileNotFoundError(f"Neither {file_path} nor {alt_path} exists")

        df = pd.read_excel(file_path, header=3)
        df = df.fillna("")
        print(f"Successfully read Excel file. Found {len(df)} rows")

        properties_data = {}
        for _, row in df.iterrows():
            try:
                if not str(row["Position"]).strip().isdigit():
                    continue

                position = int(row["Position"])
                property_name = str(row["Space/property"]).strip()

                print(f"Processing position {position}: {property_name}")

                property_data = {
                    "name": property_name,
                    "position": position,
                    "group": str(row["Group"]).strip() if row["Group"] else None,
                    "action": str(row["Action"]).strip() if row["Action"] else None,
                    "can_be_bought": str(row["Can be bought?"]).strip().lower()
                    == "yes",
                }

                # Handle special spaces
                if property_name in ["Income Tax", "Super Tax"]:
                    property_data.update(
                        {
                            "type": "tax",
                            "amount": 200 if property_name == "Income Tax" else 100,
                        }
                    )
                elif property_name in ["Jail", "Go to Jail", "Free Parking", "Go"]:
                    property_data.update({"type": "special"})
                # Handle stations
                elif "Station" in property_name:
                    property_data.update(
                        {
                            "type": "station",
                            "price": 200,
                            "rent": 25,  # Base rent, multiplied based on number of stations owned
                            "owner": None,
                            "is_station": True,
                        }
                    )
                elif property_name in ["Tesla Power Co", "Edison Water"]:
                    property_data.update(
                        {
                            "type": "utility",
                            "price": 150,
                            "rent": 0,
                            "owner": None,
                            "is_utility": True,
                        }
                    )
                elif property_data["can_be_bought"] and row["£"]:
                    try:
                        price_str = str(row["£"]).replace("£", "").strip()
                        rent_str = str(row["£.1"]).replace("£", "").strip() or "0"

                        property_data.update(
                            {
                                "type": "property",
                                "price": int(float(price_str)),
                                "rent": int(float(rent_str)),
                                "owner": None,
                                "house_costs": [],
                                "houses": 0,
                                "is_mortgaged": False,
                            }
                        )

                        for i in range(2, 7):
                            cost = row.get(f"£.{i}", "")
                            if cost and str(cost).strip():
                                try:
                                    cost_str = str(cost).replace("£", "").strip()
                                    property_data["house_costs"].append(
                                        int(float(cost_str))
                                    )
                                except (ValueError, TypeError):
                                    continue
                    except (ValueError, TypeError) as e:
                        print(f"Error processing costs for position {position}: {e}")
                        continue
                else:
                    property_data.update({"type": "special"})

                properties_data[str(position)] = property_data

            except (ValueError, TypeError) as e:
                print(f"Error processing row: {e}")
                continue

        positions_loaded = sorted([int(pos) for pos in properties_data.keys()])
        print(f"Successfully loaded properties for positions: {positions_loaded}")
        print(f"Total properties loaded: {len(properties_data)}")
        return properties_data

    except Exception as e:
        print(f"Error loading Excel file: {e}")
        import traceback

        traceback.print_exc()
        return None


def load_game_text(
    filename="assets/gamedata/PropertyTycoonCardData.xlsx", sheet_name="Game Text"
):
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(current_dir, filename)
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        card_data = {}
        for index, row in df.iterrows():
            key = row["Key"]
            text = row["Text"]
            card_data[key] = text
        print(f"Game text loaded from '{sheet_name}' sheet in Excel.")
        return card_data

    except FileNotFoundError:
        print(
            f"{filename} not found. Make sure it's in the same directory as the script."
        )
        return None
    except KeyError:
        print(f"{sheet_name}' or columns 'Key' and 'Text' not found in {filename}.")
        return None
    except Exception as e:
        print(f"Error loading card data from Excel: {e}")
        return None
