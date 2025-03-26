def run_lynis_and_save_output():
    lynis_executable = "./lynis" if os.path.isfile("./lynis") else "lynis"
    
    # Force output path to ~/lynis/lynis_report.txt
    home_dir = os.path.expanduser("~")
    report_dir = os.path.join(home_dir, "lynis")
    output_file = os.path.join(report_dir, "lynis_report.txt")

    # Create the directory if it's missing
    os.makedirs(report_dir, exist_ok=True)

    print("\n⚠️  This system audit may take a minute or two to complete. Please be patient...\n")
    print(f"🚀 Running Lynis using: {lynis_executable}")

    try:
        with open(output_file, "w") as f:
            subprocess.run(
                [lynis_executable, "audit", "system", "--no-colors", "--verbose"],
                stdout=f,
                stderr=subprocess.STDOUT,
                check=True
            )
        print(f"\n✅ Lynis audit complete.")
        print(f"📄 Output saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print("❌ Lynis failed to run.")
        print(f"Error: {e}")
