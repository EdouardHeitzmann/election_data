import glob
import regex as re
import os


def process_2007_cands(cands):
    party_dict_2007 = {
        "Scottish Unionist": "Scottish Unionist (SU)",
        "Con": "Conservative and Unionist Party (Con)",
        "LD": "Liberal Democrat (LD)",
        "Grn": "Green (Gr)",
        "SNP": "Scottish National Party (SNP)",
        "BNP": "British National Party (BNP)",
        "Ind": "Independent (Ind)",
        "CPA": "Christian Peoples Alliance (CPA)",
        "SC": "Scottish Christian (SC)",
        "Lab": "Labour (Lab)",
        "Soc": "Socialist (Soc)",
        "Sol": "Solidarity (Sol)",
    }

    name_party_pairs = []
    for c in cands:
        name = re.search(r"(?<=:\s)[A-Z,a-z\s]*", c).group()
        party = re.search(r"(?<=\()[A-Z,a-z,\s]*(?<!\))", c).group()

        name_party_pairs.append((name, party_dict_2007[party]))
    return name_party_pairs


def process_2012_2017_cands(cands):
    party_dict_2012_2017 = {
        "CICA": "Cumbernauld Independent Councillors Alliance (CICA)",
        "Scottish Unionist": "Scottish Unionist (SU)",
        "Con": "Conservative and Unionist Party (Con)",
        "Lib": "Liberal (Lib)",
        "CPA": "Christian Peoples Alliance (CPA)",
        "UKIP": "UK Independence Party (UKIP)",
        "Lab": "Labour (Lab)",
        "IANL": "Independent Alliance North Lanarkshire (IANL)",
        "SU": "Scottish Unionist (SU)",
        "SUP": "Scottish Unionist (SU)",
        "Soc": "Socialist (Soc)",
        "MVR": "Monster Raving Loony (MVR)",
        "Grn": "Green (Gr)",
        "SDP": "Social Democratic Party (SDP)",
        "SNP": "Scottish National Party (SNP)",
        "Glasgow First": "Glasgow First (Glasgow First)",
        "Scottish Socialist": "Socialist (Soc)",
        "SSP": "Socialist (Soc)",
        "Pir": "Piarate (Pir)",
        "TUSC": "Trade Unionist and Socialist Coalition (TUSC)",
        "SLP": "Socialist Labour Party (SLP)",
        "SC": "Scottish Christian (SC)",
        "Borders": "Borders (Borders)",
        "WDuns": "West Dunbartonshire Community (WDuns)",
        "SSC": "Scottish Senior Citizens (SSC)",
        "Comm": "Communist Party of Britain (Comm)",
        "NF": "National Front (NF)",
        "Rubbish": "Rubbish (Rubbish)",
        "Scotland Ind Network": "Scotland Independent Network (ScIN)",
        "LD": "Liberal Democrat (LD)",
        "BUSP": "No Referendum, Maintain Union, Pro-Brexit (NRMUPB)",
        "EKA": "East Kilbride Alliance (EKA)",
        "SU": "Scottish Unionist (SU)",
        "ind": "Independent (Ind)",
        "Sol": "Solidarity (Sol)",
        "OMG": "Orkney Manifesto Group (OMG)",
        "NRMUPB": "No Referendum, Maintain Union, Pro-Brexit (NRMUPB)",
        "Libtn": "Libertarian (Libtn)",
        "Britannica Party": "Britannica Party (BP)",
        "EDIA": "East Dunbartonshire Independent Alliance (EDIA)",
        "Ind": "Independent (Ind)",
        "SocLab": "Socialist Labour Party (SLP)",
        "IndNk": "Independent (Ind)",
        "C": "Conservative and Unionist Party (Con)",
        "Socialist Labour": "Socialist Labour Party (SLP)",
        "RISE": "RISE (RISE)",
        "Chr": "Scottish Christian (SC)",
    }

    name_party_pairs = []

    for c in cands:
        name = re.search(r"[A-Z,a-z,\.,\s]*", c)
        party = re.search(r"(?<=\()[A-Z,a-z,\s]*(?<!\))", c)

        if not name or not party:
            name = re.search(r"(?<=\"\")[A-Z,a-z,\.,\s]{2,}(?<!\"\")", c)
            party = re.search(r"(?<=^\")[A-Z,a-z,\s]*(?<!\s\")", c)

        name_party_pairs.append(
            (name.group(), party_dict_2012_2017[party.group().strip()])
        )

    return name_party_pairs


def process_2022_cands(cands):
    party_dict_2022 = {
        "Freedom Alliance. Leave Our Children Alone": "Freedom Alliance (FA)",
        "Scottish Socialist Party - End Fuel Poverty": "Socialist (Soc)",
        "Volt UK - The Pan-European Party": "Volt UK (Volt)",
        "Communist Party of Britain": "Communist Party of Britain (Comm)",
        "Aberdeen Labour": "Labour (Lab)",
        "Scottish National Party (SNP)": "Scottish National Party (SNP)",
        "Re-elect your Scottish Green Councillor": "Green (Gr)",
        "Freedom Alliance. People Power.Politics.": "Freedom Alliance (FA)",
        "Alba Party for Independence": "Alba Party for Independence (API)",
        "Vanguard Party championing Tweeddale": "Vanguard Party (Van)",
        "Independent": "Independent (Ind)",
        "UKIP": "UK Independence Party (UKIP)",
        "UK Independence Party (UKIP)": "UK Independence Party (UKIP)",
        "Women's Equality Party": "Women's Equality Party (WEP)",
        "Freedom Alliance. Leave our Children Alone.": "Freedom Alliance (FA)",
        "Scottish Trade Unionist and Socialist Coalition": "Trade Unionist and Socialist Coalition (TUSC)",
        "Scottish Green Party": "Green (Gr)",
        "Sovereignty": "Sovereignty (Sov)",
        "Freedom Alliance. Real People. Real Alternative": "Freedom Alliance (FA)",
        "Liberal Democrat Focus Team": "Liberal Democrat (LD)",
        "Scottish Socialist Party - Save Public Services": "Socialist (Soc)",
        "Scottish Greens - Delivering For Our Community": "Green (Gr)",
        "Independent (Ind)": "Independent (Ind)",
        "Scottish Labour Party": "Labour (Lab)",
        "Labour and Co-operative Party": "Labour and Co-operative Party (LabCo)",
        "Scottish Greens - Delivering for Our Community": "Green (Gr)",
        "Scottish Family Party Pro-Family, Pro-Marriage, Pro-Life": "Scottish Family Party (SFP)",
        "Scottish Socialist Party - People Not Profit": "Socialist (Soc)",
        "Scottish Greens - Think Global Act Local": "Green (Gr)",
        "Alba Party for independence": "Alba Party for Independence (API)",
        "Glasgow Labour": "Labour (Lab)",
        "Freedom Alliance. No More Experimental Jabs.": "Freedom Alliance (FA)",
        "Independence for Scotland Party": "Independence for Scotland Party (ISP)",
        "The Pensioner's Party": "The Pensioner's Party (TPP)",
        "Scottish Libertarian Party": "Libertarian (Libtn)",
        "Aberdeen Labour (Lab)": "Labour (Lab)",
        "Elect a Scottish Green Councillor": "Green (Gr)",
        "Scottish Green Party (Grn)": "Green (Gr)",
        "Social Democratic Party": "Social Democratic Party (SDP)",
        "Socialist Labour Party": "Socialist Labour Party (SLP)",
        "Indepenent (Ind)": "Independent (Ind)",
        "British Unionists - For A Better Britain": "British Unionists (BU)",
        "Scottish Family Party Pro-Family (SFP)": "Scottish Family Party (SFP)",
        "Scottish Conservative and Unionist": "Conservative and Unionist Party (Con)",
        "Scottish Conservative and Unionist (Con)": "Conservative and Unionist Party (Con)",
        "Alba Party": "Alba Party for Independence (API)",
        "Scottish Socialist Party": "Socialist (Soc)",
        "Scottish Liberal Democrats": "Liberal Democrat (LD)",
        "Alba Party for Scottish independence": "Alba Party for Independence (API)",
        "Scottish Trade Unionist and Socialist Coalition (Soc)": "Trade Unionist and Socialist Coalition (TUSC)",
        "Scottish Greens": "Green (Gr)",
        "Scottish Liberal Democrats (LD)": "Liberal Democrat (LD)",
        "Scottish Family Party": "Scottish Family Party (SFP)",
        "Scottish Family Party (SFP)": "Scottish Family Party (SFP)",
        "Alba Party for independence (API)": "Alba Party for Independence (API)",
        "Labour and Co-Operative Party": "Labour and Co-operative Party (LabCo)",
        "Scottish Liberal Democrat Focus Team": "Liberal Democrat (LD)",
        "(Ind)": "Independent (Ind)",
        "Freedom Alliance. Leave Our Children Alone.": "Freedom Alliance (FA)",
        "Freedom Alliance. Stop the Great Reset.": "Freedom Alliance (FA)",
        "Freedom Alliance. Truth, Equality and Health.": "Freedom Alliance (FA)",
        "Labour and Co": "Labour and Co-operative Party (LabCo)",
        "S cottish Liberal Democrats": "Liberal Democrat (LD)",
        "Scottish Eco-Federalist Party (SEFP)": "Scottish Eco-Federalist Party (SEFP)",
        "Scottish Family Party Pro": "Scottish Family Party (SFP)",
        "The Rubbish Party": "Rubbish (Rubbish)",
        "Vanguard Party championing Kelso": "Vanguard Party (Van)",
        "Vanguard Party championing Leaderdale and Melrose": "Vanguard Party (Van)",
        "West Dunbartonshire Community Party": "West Dunbartonshire Community (WDuns)",
        "Your local Alba Party independence champion": "Alba Party for Independence (API)",
        "Workers Party of Britain": "Worker Party of Britain (WPB)",
        "Vanguard Party championing Galashiels": "Vanguard Party (Van)",
    }
    name_party_pairs = []

    for c in cands:
        name_and_party = re.findall(r"(?<=\")[A-Z,a-z,\',\.,\-,\(,\),\s]*(?<!\")", c)

        name_and_party = [x for x in name_and_party if x.strip() != ""]

        name = name_and_party[0]
        party = name_and_party[-1]

        name_party_pairs.append((name, party_dict_2022[party.strip()]))

    return name_party_pairs


def process_file_list(file_list, output_dir, processing_function):
    for file in file_list:
        if "_by_" in file:
            continue

        write_lines = []

        with open(file, "r") as f:
            lines = [line.strip("\n").strip() for line in f.readlines()]
            n_cands = lines[0].split(" ")[0]
            cands = lines[-int(n_cands) - 1 : -1]
            first_line = ",".join(lines[0].split(" ")) + ",\n"
            write_lines.append(first_line)
            for idx in range(1, len(lines) - int(n_cands) - 2):
                write_lines.append(
                    ",".join(lines[idx].rstrip()[:-2].split(" ")) + ",\n"
                )

            for i, (name, party) in enumerate(processing_function(cands)):
                write_lines.append(
                    f'"Candidate {i+1}","{name.strip().title()}","{party.strip()}",\n'
                )

            write_lines.append(f'"{lines[-1]}",')

        file_name, _ext = os.path.splitext(os.path.basename(file))
        file_parent = os.path.basename(os.path.dirname(file))
        out_file = os.path.join(output_dir, file_parent, file_name + ".csv")
        print(out_file)
        with open(out_file, "w") as f:
            f.writelines(write_lines)


if __name__ == "__main__":
    year_to_func = {
        2007: process_2007_cands,
        2012: process_2012_2017_cands,
        2017: process_2012_2017_cands,
        2022: process_2022_cands,
    }

    for year, processing_func in year_to_func.items():
        file_list = glob.glob(f"./blt_files/**/*{year}*.blt")

        process_file_list(
            file_list=file_list, output_dir="./", processing_function=processing_func
        )
