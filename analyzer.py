import pandas as pd
import matplotlib.pyplot as plt
import logging

LOG_FILE = "logs/server_logs.csv"

def main():
    # ---------------- LOGGING ----------------
    logging.basicConfig(
        filename="execution.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Log File Analyzer Started")

    valid_rows = []
    invalid_lines = 0

    # ---------------- READ LOG FILE SAFELY ----------------
    with open(LOG_FILE, "r") as file:
        file.readline()  # skip header
        for line in file:
            try:
                parts = line.strip().split(",")
                if len(parts) != 4:
                    raise ValueError("Invalid format")

                timestamp, ip, request, error_code = parts
                error_code = int(error_code)

                valid_rows.append([timestamp, ip, request, error_code])

            except Exception:
                invalid_lines += 1
                logging.warning(f"Invalid log entry skipped: {line.strip()}")

    # ---------------- CREATE DATAFRAME ----------------
    df = pd.DataFrame(
        valid_rows,
        columns=["timestamp", "ip", "request", "error_code"]
    )

    total_requests = len(df)
    error_df = df[df["error_code"] >= 400]
    total_errors = len(error_df)

    error_counts = error_df["error_code"].value_counts()
    top_ips = error_df["ip"].value_counts().head(5)

    # ---------------- SUMMARY REPORT ----------------
    with open("output/summary_report.txt", "w") as f:
        f.write("LOG FILE ANALYSIS REPORT\n")
        f.write("========================\n")
        f.write(f"Total Requests : {total_requests}\n")
        f.write(f"Total Errors   : {total_errors}\n")
        f.write(f"Invalid Lines  : {invalid_lines}\n\n")
        f.write("Error Code Frequency:\n")
        f.write(error_counts.to_string())
        f.write("\n\nTop 5 IPs with Errors:\n")
        f.write(top_ips.to_string())

    # ---------------- TERMINAL OUTPUT ----------------
    print("\n📊 LOG FILE ANALYSIS SUMMARY")
    print("----------------------------")
    print(f"Total Requests : {total_requests}")
    print(f"Total Errors   : {total_errors}")
    print(f"Invalid Lines  : {invalid_lines}")
    print("\nError Codes:\n", error_counts)
    print("\nTop 5 IPs:\n", top_ips)

    # ====================================================
    # 📊 BIG & DETAILED CHART 1: ERROR CODE DISTRIBUTION
    # ====================================================
    plt.figure(figsize=(10, 6))
    ax1 = error_counts.plot(
        kind="bar",
        color=["#d62728", "#ff7f0e", "#9467bd"],
        edgecolor="black"
    )

    plt.title("HTTP Error Code Distribution", fontsize=16, fontweight="bold")
    plt.xlabel("Error Code", fontsize=12)
    plt.ylabel("Number of Errors", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    for bar in ax1.patches:
        ax1.annotate(
            str(bar.get_height()),
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.tight_layout()
    plt.savefig("output/error_distribution_detailed.png")

    # ====================================================
    # 📊 BIG & DETAILED CHART 2: TOP 5 IP ADDRESSES
    # ====================================================
    plt.figure(figsize=(10, 6))
    ax2 = top_ips.plot(
        kind="bar",
        color="#1f77b4",
        edgecolor="black"
    )

    plt.title("Top 5 IP Addresses Generating Errors", fontsize=16, fontweight="bold")
    plt.xlabel("IP Address", fontsize=12)
    plt.ylabel("Error Count", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    for bar in ax2.patches:
        ax2.annotate(
            str(bar.get_height()),
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.tight_layout()
    plt.savefig("output/top_5_ips_detailed.png")

    logging.info("Log analysis completed successfully")
    print("\n✅ Analysis complete. Detailed reports and charts generated.")

# ---------------- MAIN GUARD ----------------
if __name__ == "__main__":
    main()
