from weather_client import poll_weather

def main():
    results = poll_weather()
    for data in results:
        location = data["location"]["name"]
        country = data["location"]["country"]
        current = data["current"]

        print(f"{location}, {country}")
        print(f"  Temp: {current['temperature']}°C")
        print(f"  Desc: {', '.join(current['weather_descriptions'])}")
        print(f"  Humidity: {current['humidity']}%")
        print()

if __name__ == "__main__":
    main()
