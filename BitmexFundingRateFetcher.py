import csv
import requests
import time
import datetime
import xlsxwriter


# configuration
base_URL = "https://www.bitmex.com/api/v1"
endpoint = "/funding"
asset = "ETHUSD"
start_date = "2022-01-01 00:00"
end_date = "2023-01-01 00:00"


# Request Rate Limits are 120 Requests per minute reduced to 30 when unauthenticated
def throttle_api(unix_timecode):
    rate_limit = 2
    current_time = time.time()
    time_to_wait = rate_limit - (current_time - unix_timecode)
    if time_to_wait > 0:
        print(f"waiting for {time_to_wait} seconds")
        time.sleep(time_to_wait)


def get_http_response(URL):
    try:
        response = requests.get(URL)
    except Exception as exception:
        print(f"ERROR(BitMEX): status code {str(exception)}")
        raise Exception
    return response


def check_request_status(status_code):
    if status_code != 200:
        print(f"ERROR(BitMEX): status code {status_code}")
        raise Exception


def get_last_timestamp_from_dataset(data):
    data_length = len(data)
    last_date = (data[data_length - 1])["timestamp"]
    return last_date


def format_dataset_timestamp(data_timestamp):
    formatted_timestamp = ""
    for char in data_timestamp:
        if char == "T":
            formatted_timestamp += " "
        else:
            formatted_timestamp += char
    return formatted_timestamp[0:16]


def format_date_for_URL(date_string_with_whitespaces_and_colons):
    formatted_date = ""
    for char in date_string_with_whitespaces_and_colons:
        if char == " ":
            formatted_date += "%20"
        elif char == ":":
            formatted_date += "%3A"
        else:
            formatted_date += char
    return formatted_date


# using the UNIX-Timecode to check if another API-Call is required in the fetch_data methode
# this is necessary because BitMEX doesn't offer a "last-ID" for calling the next request and comparing date-strings is useless
# expected format is 'yyyy_mm_dd hh:mm'
def date_string_to_unix_timecode(date_string):
    date_and_time = date_string.split()
    date = date_and_time[0]
    time = date_and_time[1]
    date_split = date.split("-")
    time_split = time.split(":")
    year, month, day = date_split
    hour, minute = time_split

    unix_timecode = datetime.datetime(
        int(year), int(month), int(day), int(hour), int(minute)
    ).timestamp()
    return int(unix_timecode)


def write_data_to_csv(data_list):
    csv_header = [
        "timestamp",
        "symbol",
        "fundingInterval",
        "fundingRate",
        "fundingRateDaily",
    ]
    if data_list:
        with open(
            f"BitMEX_funding_rate_{asset}_{start_date}_{end_date}.csv", "w"
        ) as stream:
            writer = csv.writer(stream)
            writer.writerow(csv_header)
            writer.writerows(data_list)


def write_data_to_xlsx(data_list):
    workbook = xlsxwriter.Workbook(
        f"BitMEX_funding_rate_{asset}_{start_date}_{end_date}.xlsx"
    )
    worksheet = workbook.add_worksheet(f"funding_rate_{asset}")

    # initializing table, filling with header
    row = 0
    colum = 0
    worksheet.write(row, colum, "timestamp")
    worksheet.write(row, colum + 1, "symbol")
    worksheet.write(row, colum + 2, "fundingInterval")
    worksheet.write(row, colum + 3, "fundingRate")
    worksheet.write(row, colum + 4, "fundingRateDaily")
    row += 1

    # printing data to table
    for timestamp, symbol, fundingInterval, fundingRate, fundingRateDaily in data_list:
        worksheet.write(row, colum, timestamp)
        worksheet.write(row, colum + 1, symbol)
        worksheet.write(row, colum + 2, fundingInterval)
        worksheet.write(row, colum + 3, fundingRate)
        worksheet.write(row, colum + 4, fundingRateDaily)
        row += 1

    workbook.close()


# every API call creates one doubled element.
def filter_double_entries(data_list):
    filtered_data_array = []
    filtered_data_array.append(data_list[0])

    for i in range(1, len(data_list)):
        if (data_list[i - 1])[0] == (data_list[i])[0]:
            continue
        filtered_data_array.append(data_list[i])

    return filtered_data_array


def fetch_data(start_date, end_date):
    request_date = format_date_for_URL(start_date)
    request_date_unix_timecode = date_string_to_unix_timecode(start_date)
    end_date_unix_timecode = date_string_to_unix_timecode(end_date)

    data_list = []

    while request_date_unix_timecode <= end_date_unix_timecode:
        current_time = time.time()
        response = get_http_response(
            f"{base_URL}{endpoint}?symbol={asset}&count=500&reverse=false&startTime={request_date}"
        )
        check_request_status(response.status_code)
        data = response.json()

        # getting last timestamp from dataset, formatting it twice to Unix-timestamp and next URL-string for next call
        last_timestamp = get_last_timestamp_from_dataset(data)
        last_timestamp_formatted = format_dataset_timestamp(last_timestamp)
        request_date = format_date_for_URL(last_timestamp_formatted)
        request_date_unix_timecode = date_string_to_unix_timecode(
            last_timestamp_formatted
        )
        for entry in data:
            entry_unix_timecode = date_string_to_unix_timecode(
                format_dataset_timestamp(entry["timestamp"])
            )
            if entry_unix_timecode <= end_date_unix_timecode:
                extracted_data = [
                    entry["timestamp"],
                    entry["symbol"],
                    entry["fundingInterval"],
                    entry["fundingRate"],
                    entry["fundingRateDaily"],
                ]
                data_list.append(extracted_data)

        throttle_api(current_time)
    return data_list


data_list = fetch_data(start_date, end_date)
funding_rates = filter_double_entries(data_list)
# write_data_to_xlsx(funding_rates)
write_data_to_csv(funding_rates)
print("done")
