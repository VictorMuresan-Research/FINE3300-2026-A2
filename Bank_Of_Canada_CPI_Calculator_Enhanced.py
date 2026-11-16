"""Enhanced inflation calculator based on monthly Bank of Canada CPI data."""

# NumPy is used for the average annual inflation calculation.
import numpy as np

# Pandas reads and organizes the CPI data from the CSV file.
import pandas as pd

# Matplotlib creates and saves the CPI graph.
import matplotlib.pyplot as plt


def get_amount():
    # This function asks for the price and checks that it is a valid number.
    # The loop repeats if the user enters text or an amount of zero or less.
    while True:
        amount_text = input("Enter the price of the goods or services: $")

        # Remove dollar signs, commas, and spaces so float() can read the amount.
        amount_text = amount_text.replace("$", "").replace(",", "").replace(" ", "")

        try:
            # Convert the user's text to a number.
            amount = float(amount_text)
            if amount > 0:
                # Return the valid amount to the main program.
                return amount
            else:
                print("Please enter an amount greater than zero.")
        except ValueError:
            # float() causes a ValueError if the text is not a valid number.
            print("Please enter a valid number, such as 100000 or 100,000.00.")


def get_period(prompt, monthly_cpi):
    # Find the first and last dates that have CPI data.
    first_date = monthly_cpi.index.min()
    last_date = monthly_cpi.index.max()

    # Ask for a month and year in MM/YYYY format until a valid data period is entered.
    while True:
        date_text = input(prompt)

        # Convert the entered text to a date. An invalid date becomes NaT,
        # which means "Not a Time" in Pandas.
        period = pd.to_datetime(date_text, format="%m/%Y", errors="coerce")

        # Check whether the user entered a correctly formatted date.
        if pd.isna(period):
            print("Please enter a valid month and year in MM/YYYY format.")
        # Check that the date is not earlier or later than the available data.
        elif period < first_date or period > last_date:
            print("Enter a date between {} and {}.".format(
                first_date.strftime("%m/%Y"), last_date.strftime("%m/%Y")
            ))
        # Check that the exact month is in the CPI data.
        elif period not in monthly_cpi.index:
            print("There is no CPI value for that month in the data.")
        else:
            # Return the valid date to the main program.
            return period


# This condition makes the calculator run when this file is started directly.
# It prevents the prompts and graph from appearing if the file is imported elsewhere.
if __name__ == "__main__":

    # Read the Bank of Canada CPI data into a data frame.
    # The first 8 rows of the CSV file contain information about the data.
    df = pd.read_csv("STATIC_INFLATIONCALC.csv", skiprows=8)

    # Keep only the date and CPI columns because the other columns are not needed.
    df = df[["date", "STATIC_INFLATIONCALC"]]

    # Rename the columns to shorter names that are easier to use in the code.
    df = df.rename(columns={"date": "Date", "STATIC_INFLATIONCALC": "CPI"})

    # Convert the date text to dates and the CPI values to numbers.
    # This lets Pandas work with the dates and CPI values correctly.
    df["Date"] = pd.to_datetime(df["Date"])
    df["CPI"] = pd.to_numeric(df["CPI"])

    # Set the dates as the data frame index so a CPI value can be found by month.
    df = df.set_index("Date")

    # Select the CPI column and sort dates from oldest to newest.
    monthly_cpi = df["CPI"].sort_index()

    # Ask for a valid price and two valid month/year periods.
    amount = get_amount()
    first_period = get_period("Enter the first period (MM/YYYY): ", monthly_cpi)
    second_period = get_period("Enter the second period (MM/YYYY): ", monthly_cpi)

    # Look up the CPI value for each date entered by the user.
    cpi1 = monthly_cpi.loc[first_period]
    cpi2 = monthly_cpi.loc[second_period]

    # Adjust the original amount using the ratio of the second CPI to the first CPI.
    adjusted_cost = amount * (cpi2 / cpi1)

    # Calculate the percentage change from the original amount to the adjusted amount.
    percentage_change = ((adjusted_cost - amount) / amount) * 100

    # Find the number of whole months between the selected periods.
    month_difference = (second_period.year - first_period.year) * 12
    month_difference = month_difference + second_period.month - first_period.month

    # Convert the month difference to years. Use the absolute value so the duration
    # is positive even if the second period is earlier than the first period.
    number_of_years = abs(month_difference) / 12

    # Calculate the average annual rate of inflation over the selected time period.
    # If both periods are the same, there is no time interval over which to calculate a rate.
    if number_of_years == 0:
        average_annual_rate = 0.0
    else:
        # np.power() raises the CPI ratio to the power of 1 / number of years.
        # Subtract 1 and multiply by 100 to express the result as a percentage.
        average_annual_rate = (np.power(cpi2 / cpi1, 1 / number_of_years) - 1) * 100

    # Print the results in the Bank of Canada calculator format.
    print()
    print('A "basket" of goods and services')
    print("...that cost:")
    print("${:,.2f} CAD in {}".format(amount, first_period.strftime("%B %Y")))
    print()
    print("...would cost:")
    print("${:,.2f} CAD in {}".format(adjusted_cost, second_period.strftime("%B %Y")))
    print()
    print("Percent change: {:.2f}%".format(percentage_change))
    if month_difference % 12 == 0:
        print("Number of years: {}".format(abs(month_difference) // 12))
    else:
        print("Number of years: {:.2f}".format(number_of_years))
    print("Average annual rate of inflation (%) / Decline in the value of money: {:.2f}%".format(average_annual_rate))
    print("CPI for first period: {:.1f}".format(cpi1))
    print("CPI for second period: {:.1f}".format(cpi2))
    print("2002 CPI = 100.0")

    # Calculate annual inflation for each month by comparing it with the same month
    # one year earlier. A 12-month difference gives the year-over-year change.
    annual_change = monthly_cpi.pct_change(periods=12) * 100

    # Plot the monthly CPI and annual percentage change.
    fig, ax1 = plt.subplots(figsize=(10, 5))
    cpi_line, = ax1.plot(monthly_cpi.index, monthly_cpi.values, label="Monthly CPI")

    # Add a dotted horizontal line at the CPI base level of 100.0.
    base_line = ax1.axhline(
        y=100.0,
        color="gray",
        linestyle=":",
        label="Base level (2002 = 100.0)"
    )

    # Label the horizontal axis, vertical axis, and graph.
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Consumer Price Index (CPI)")
    ax1.set_title("Canadian CPI and Annual Percentage Change", fontsize=16)

    # Make a second y-axis so the percentage change can use its own scale.
    ax2 = ax1.twinx()
    change_line, = ax2.plot(
        annual_change.index,
        annual_change.values,
        color="darkorange",
        label="Annual percentage change"
    )
    ax2.set_ylabel("Annual percentage change (%)")

    # Add a legend for all three lines.
    lines = [cpi_line, base_line, change_line]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="upper left")

    # Adjust spacing so the labels and title fit in the figure.
    fig.tight_layout()

    # Save the graph as a PNG image, then display it.
    fig.savefig("inflation_cpi_chart.png")
    plt.show()