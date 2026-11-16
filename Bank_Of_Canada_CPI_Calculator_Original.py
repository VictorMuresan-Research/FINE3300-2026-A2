"""Original inflation calculator based on yearly (September) Bank of Canada CPI data."""

# NumPy is used for numerical calculations.
import numpy as np

# Pandas reads and organizes the CPI data from the CSV file.
import pandas as pd

# Matplotlib creates and saves the CPI graph.
import matplotlib.pyplot as plt


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

    # Create separate columns for the year and month of each observation.
    # The month column lets us select September CPI values.
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    # Keep only September observations because the Bank of Canada calculator
    # uses September CPI values when comparing one year with another.
    september_cpi = df[df["Month"] == 9]

    # Group the September observations by year and get each year's CPI value.
    annual_cpi = september_cpi.groupby("Year")["CPI"].mean()

    # Calculate the percentage change in September CPI from one year to the next.
    # pct_change() finds the change as a proportion, multiplying by 100 converts it to percent.
    annual_change = annual_cpi.pct_change() * 100

    # Ask the user for a dollar amount.
    # Remove commas and spaces before converting the text to a number.
    amount = input("Enter a dollar amount (commas and spaces may be used): $")
    amount = float(amount.replace(",", "").replace(" ", ""))

    # Find the latest year available in the CPI data.
    # Use it in the prompts so the user knows the available year range.
    latest_year = annual_cpi.index.max()

    # Ask the user which two years to compare, then convert the answers to integers.
    first_year = int(input("Enter the first year (1914 to {}): ".format(latest_year)))
    second_year = int(input("Enter the second year (1914 to {}): ".format(latest_year)))

    # Look up the September CPI value for each selected year.
    cpi1 = annual_cpi.loc[first_year]
    cpi2 = annual_cpi.loc[second_year]

    # Adjust the original amount using the ratio of the second CPI to the first CPI.
    adjusted_cost = amount * (cpi2 / cpi1)

    # Calculate the percentage change from the original amount to the adjusted amount.
    percentage_change = ((adjusted_cost - amount) / amount) * 100
    
    # Calculate the number of years between the two selected years.
    # abs() makes the number positive if the years are entered in reverse order.
    number_of_years = abs(second_year - first_year)

    # Calculate the average annual rate of inflation.
    # If both years are the same, the rate is set to zero because there is no time interval.
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
    print("${:,.2f} CAD in {}".format(amount, first_year))
    print()
    print("...would cost:")
    print("${:,.2f} CAD in {}".format(adjusted_cost, second_year))
    print()
    print("Percent change: {:.2f}%".format(percentage_change))
    print("Number of years: {}".format(number_of_years))
    print("Average annual rate of inflation (%) / Decline in the value of money: {:.2f}%".format(average_annual_rate))
    print("CPI for first year: {:.1f}".format(cpi1))
    print("CPI for second year: {:.1f}".format(cpi2))
    print("2002 CPI = 100.0")

    # Create a figure and the first set of axes for the CPI line.
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Plot September CPI values over time.
    # Keep the line so it can be included in the legend later.
    cpi_line, = ax1.plot(annual_cpi.index, annual_cpi.values, label="September CPI")

    # Draw a dotted horizontal line at 100, the CPI base level for 2002.
    # Keep this line so it can also be included in the legend.
    base_line = ax1.axhline(
        y=100.0,
        color="gray",
        linestyle=":",
        label="Base level (2002 = 100.0)"
    )

    # Label the horizontal axis, vertical axis, and graph.
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Consumer Price Index (CPI, September)")
    ax1.set_title("Canadian September CPI and Annual Percentage Change", fontsize=16)

    # Create a second vertical axis for annual percentage change.
    # A second axis lets the CPI and percentage values use different scales.
    ax2 = ax1.twinx()

    # Plot the annual percentage change on the second vertical axis.
    # Keep the line so it can be included in the legend.
    change_line, = ax2.plot(
        annual_change.index,
        annual_change.values,
        color="darkorange",
        label="Annual percentage change"
    )

    # Label the right-hand vertical axis.
    ax2.set_ylabel("Annual percentage change (%)")

    # Combine the three plotted lines so they all appear in one legend.
    lines = [cpi_line, base_line, change_line]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="upper left")

    # Adjust spacing so the labels and title fit in the figure.
    fig.tight_layout()

    # Save the graph as a PNG image, then display it.
    fig.savefig("inflation_cpi_chart.png")
    plt.show()